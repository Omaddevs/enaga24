from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, path: str) -> None:
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.conn.execute("PRAGMA journal_mode = WAL")
        await self._init()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None

    def _c(self) -> aiosqlite.Connection:
        assert self.conn is not None
        return self.conn

    async def _init(self) -> None:
        c = self._c()
        await c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                lang TEXT,
                phone TEXT,
                created_at TEXT NOT NULL,
                last_active TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                payload TEXT NOT NULL,
                body TEXT NOT NULL,
                photo_id TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                reject_reason TEXT,
                created_at TEXT NOT NULL,
                reviewed_at TEXT,
                reviewer_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS destinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                chat_id INTEGER NOT NULL UNIQUE,
                chat_type TEXT NOT NULL,
                username TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER,
                dest_id INTEGER,
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                views INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (listing_id) REFERENCES listings(id),
                FOREIGN KEY (dest_id) REFERENCES destinations(id)
            );

            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                chat_id INTEGER NOT NULL UNIQUE,
                username TEXT,
                invite_link TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                kind TEXT NOT NULL,
                payload TEXT NOT NULL,
                sent_ok INTEGER DEFAULT 0,
                sent_fail INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS broadcast_reads (
                broadcast_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                read_at TEXT NOT NULL,
                PRIMARY KEY (broadcast_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS bot_admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                added_by INTEGER,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                text TEXT,
                file_id TEXT,
                from_chat_id INTEGER,
                from_message_id INTEGER,
                dest_id INTEGER,
                dest_title TEXT NOT NULL,
                scheduled_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                sent_at TEXT
            );
            """
        )
        await c.commit()

    async def upsert_user(
        self,
        user_id: int,
        username: str | None,
        full_name: str,
        lang: str | None = None,
    ) -> dict[str, Any]:
        c = self._c()
        now = _now()
        await c.execute(
            """
            INSERT INTO users (user_id, username, full_name, lang, created_at, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,
                last_active=excluded.last_active,
                lang=COALESCE(excluded.lang, users.lang)
            """,
            (user_id, username, full_name, lang, now, now),
        )
        await c.commit()
        return await self.get_user(user_id)  # type: ignore

    async def extra_admins(self) -> list[dict[str, Any]]:
        cur = await self._c().execute("SELECT * FROM bot_admins ORDER BY created_at")
        return [dict(r) for r in await cur.fetchall()]

    async def all_admin_ids(self, env_admins: list[int]) -> list[int]:
        ids: list[int] = []
        seen: set[int] = set()
        extra = [int(r["user_id"]) for r in await self.extra_admins()]
        for uid in list(env_admins) + extra:
            uid = int(uid)
            if uid not in seen:
                seen.add(uid)
                ids.append(uid)
        return ids

    async def is_admin(self, user_id: int, env_admins: list[int]) -> bool:
        if user_id in env_admins:
            return True
        cur = await self._c().execute(
            "SELECT 1 FROM bot_admins WHERE user_id=?", (user_id,)
        )
        return await cur.fetchone() is not None

    async def add_admin(
        self,
        user_id: int,
        username: str | None,
        full_name: str | None,
        added_by: int,
    ) -> None:
        await self._c().execute(
            """
            INSERT INTO bot_admins (user_id, username, full_name, added_by, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name
            """,
            (user_id, username, full_name, added_by, _now()),
        )
        await self._c().commit()

    async def delete_admin(self, user_id: int) -> None:
        await self._c().execute("DELETE FROM bot_admins WHERE user_id=?", (user_id,))
        await self._c().commit()

    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        name = username.lstrip("@").strip()
        cur = await self._c().execute(
            "SELECT * FROM users WHERE LOWER(username)=LOWER(?) LIMIT 1",
            (name,),
        )
        row = await cur.fetchone()
        return dict(row) if row else None

    async def set_lang(self, user_id: int, lang: str) -> None:
        await self._c().execute(
            "UPDATE users SET lang=?, last_active=? WHERE user_id=?",
            (lang, _now(), user_id),
        )
        await self._c().commit()

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        cur = await self._c().execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def user_ids(self) -> list[int]:
        cur = await self._c().execute("SELECT user_id FROM users")
        return [r[0] for r in await cur.fetchall()]

    async def add_listing(
        self,
        user_id: int,
        category: str,
        payload: dict[str, Any],
        body: str,
        photo_id: str | None,
    ) -> int:
        cur = await self._c().execute(
            """
            INSERT INTO listings (user_id, category, payload, body, photo_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """,
            (user_id, category, json.dumps(payload, ensure_ascii=False), body, photo_id, _now()),
        )
        await self._c().commit()
        return int(cur.lastrowid)

    async def get_listing(self, listing_id: int) -> dict[str, Any] | None:
        cur = await self._c().execute("SELECT * FROM listings WHERE id=?", (listing_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def update_listing_content(
        self,
        listing_id: int,
        body: str,
        photo_id: str | None = None,
        update_photo: bool = False,
    ) -> None:
        if update_photo:
            await self._c().execute(
                "UPDATE listings SET body=?, photo_id=? WHERE id=?",
                (body, photo_id, listing_id),
            )
        else:
            await self._c().execute(
                "UPDATE listings SET body=? WHERE id=?",
                (body, listing_id),
            )
        await self._c().commit()

    async def user_listings(self, user_id: int, limit: int = 12) -> list[dict[str, Any]]:
        cur = await self._c().execute(
            "SELECT * FROM listings WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        return [dict(r) for r in await cur.fetchall()]

    async def pending_listings(self) -> list[dict[str, Any]]:
        cur = await self._c().execute(
            "SELECT * FROM listings WHERE status='pending' ORDER BY id ASC"
        )
        return [dict(r) for r in await cur.fetchall()]

    async def set_listing_status(
        self,
        listing_id: int,
        status: str,
        reviewer_id: int,
        reason: str | None = None,
    ) -> None:
        await self._c().execute(
            """
            UPDATE listings SET status=?, reviewer_id=?, reject_reason=?, reviewed_at=?
            WHERE id=?
            """,
            (status, reviewer_id, reason, _now(), listing_id),
        )
        await self._c().commit()

    async def add_destination(
        self, title: str, chat_id: int, chat_type: str, username: str | None
    ) -> int:
        cur = await self._c().execute(
            """
            INSERT INTO destinations (title, chat_id, chat_type, username, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                title=excluded.title,
                chat_type=excluded.chat_type,
                username=excluded.username,
                is_active=1
            """,
            (title, chat_id, chat_type, username, _now()),
        )
        await self._c().commit()
        return int(cur.lastrowid)

    async def destinations(self, active_only: bool = True) -> list[dict[str, Any]]:
        sql = "SELECT * FROM destinations"
        if active_only:
            sql += " WHERE is_active=1"
        sql += " ORDER BY id"
        cur = await self._c().execute(sql)
        return [dict(r) for r in await cur.fetchall()]

    async def get_destination(self, dest_id: int) -> dict[str, Any] | None:
        cur = await self._c().execute("SELECT * FROM destinations WHERE id=?", (dest_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def delete_destination(self, dest_id: int) -> None:
        await self._c().execute("DELETE FROM destinations WHERE id=?", (dest_id,))
        await self._c().commit()

    async def add_post(
        self,
        listing_id: int | None,
        dest_id: int | None,
        chat_id: int,
        message_id: int,
        views: int = 0,
    ) -> int:
        cur = await self._c().execute(
            """
            INSERT INTO posts (listing_id, dest_id, chat_id, message_id, views, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (listing_id, dest_id, chat_id, message_id, views, _now()),
        )
        await self._c().commit()
        return int(cur.lastrowid)

    async def recent_posts(self, limit: int = 20) -> list[dict[str, Any]]:
        cur = await self._c().execute(
            """
            SELECT p.*, d.title AS dest_title
            FROM posts p
            LEFT JOIN destinations d ON d.id = p.dest_id
            ORDER BY p.id DESC LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in await cur.fetchall()]

    async def get_post(self, post_id: int) -> dict[str, Any] | None:
        cur = await self._c().execute("SELECT * FROM posts WHERE id=?", (post_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def set_post_views(self, post_id: int, views: int) -> None:
        await self._c().execute("UPDATE posts SET views=? WHERE id=?", (views, post_id))
        await self._c().commit()

    async def add_subscription(
        self,
        title: str,
        chat_id: int,
        username: str | None,
        invite_link: str | None,
    ) -> int:
        cur = await self._c().execute(
            """
            INSERT INTO subscriptions (title, chat_id, username, invite_link, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                title=excluded.title,
                username=excluded.username,
                invite_link=excluded.invite_link,
                is_active=1
            """,
            (title, chat_id, username, invite_link, _now()),
        )
        await self._c().commit()
        return int(cur.lastrowid)

    async def subscriptions(self) -> list[dict[str, Any]]:
        cur = await self._c().execute(
            "SELECT * FROM subscriptions WHERE is_active=1 ORDER BY id"
        )
        return [dict(r) for r in await cur.fetchall()]

    async def delete_subscription(self, sub_id: int) -> None:
        await self._c().execute("DELETE FROM subscriptions WHERE id=?", (sub_id,))
        await self._c().commit()

    async def add_broadcast(self, admin_id: int, kind: str, payload: dict[str, Any]) -> int:
        cur = await self._c().execute(
            """
            INSERT INTO broadcasts (admin_id, kind, payload, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (admin_id, kind, json.dumps(payload, ensure_ascii=False), _now()),
        )
        await self._c().commit()
        return int(cur.lastrowid)

    async def finish_broadcast(self, broadcast_id: int, ok: int, fail: int) -> None:
        await self._c().execute(
            "UPDATE broadcasts SET sent_ok=?, sent_fail=? WHERE id=?",
            (ok, fail, broadcast_id),
        )
        await self._c().commit()

    async def mark_read(self, broadcast_id: int, user_id: int) -> int:
        await self._c().execute(
            """
            INSERT OR IGNORE INTO broadcast_reads (broadcast_id, user_id, read_at)
            VALUES (?, ?, ?)
            """,
            (broadcast_id, user_id, _now()),
        )
        await self._c().commit()
        cur = await self._c().execute(
            "SELECT COUNT(*) FROM broadcast_reads WHERE broadcast_id=?",
            (broadcast_id,),
        )
        row = await cur.fetchone()
        return int(row[0]) if row else 0

    async def stats(self) -> dict[str, Any]:
        c = self._c()
        users = (await (await c.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
        today = (
            await (
                await c.execute(
                    "SELECT COUNT(*) FROM users WHERE date(created_at)=date('now')"
                )
            ).fetchone()
        )[0]
        total = (await (await c.execute("SELECT COUNT(*) FROM listings")).fetchone())[0]
        pending = (
            await (
                await c.execute("SELECT COUNT(*) FROM listings WHERE status='pending'")
            ).fetchone()
        )[0]
        approved = (
            await (
                await c.execute("SELECT COUNT(*) FROM listings WHERE status='approved'")
            ).fetchone()
        )[0]
        rejected = (
            await (
                await c.execute("SELECT COUNT(*) FROM listings WHERE status='rejected'")
            ).fetchone()
        )[0]
        cat_rows = await (
            await c.execute(
                "SELECT category, status, COUNT(*) AS n FROM listings GROUP BY category, status"
            )
        ).fetchall()
        dest_rows = await (
            await c.execute(
                """
                SELECT d.title, COUNT(p.id) AS n
                FROM destinations d
                LEFT JOIN posts p ON p.dest_id = d.id
                GROUP BY d.id
                """
            )
        ).fetchall()
        return {
            "users": users,
            "today": today,
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "by_cat": [dict(r) for r in cat_rows],
            "by_dest": [dict(r) for r in dest_rows],
        }

    async def add_scheduled_post(
        self,
        admin_id: int,
        content_type: str,
        text: str | None,
        file_id: str | None,
        from_chat_id: int | None,
        from_message_id: int | None,
        dest_id: int | None,
        dest_title: str,
        scheduled_at: str,
    ) -> int:
        cur = await self._c().execute(
            """
            INSERT INTO scheduled_posts
                (admin_id, content_type, text, file_id, from_chat_id, from_message_id,
                 dest_id, dest_title, scheduled_at, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (
                admin_id,
                content_type,
                text,
                file_id,
                from_chat_id,
                from_message_id,
                dest_id,
                dest_title,
                scheduled_at,
                _now(),
            ),
        )
        await self._c().commit()
        return int(cur.lastrowid)

    async def get_scheduled_post(self, sched_id: int) -> dict[str, Any] | None:
        cur = await self._c().execute("SELECT * FROM scheduled_posts WHERE id=?", (sched_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def pending_scheduled_posts(self, admin_id: int | None = None) -> list[dict[str, Any]]:
        if admin_id is None:
            cur = await self._c().execute(
                "SELECT * FROM scheduled_posts WHERE status='pending' ORDER BY scheduled_at ASC"
            )
        else:
            cur = await self._c().execute(
                """
                SELECT * FROM scheduled_posts
                WHERE status='pending' AND admin_id=?
                ORDER BY scheduled_at ASC
                """,
                (admin_id,),
            )
        return [dict(r) for r in await cur.fetchall()]

    async def due_scheduled_posts(self, now_utc: str) -> list[dict[str, Any]]:
        cur = await self._c().execute(
            "SELECT * FROM scheduled_posts WHERE status='pending' AND scheduled_at<=? ORDER BY scheduled_at ASC",
            (now_utc,),
        )
        return [dict(r) for r in await cur.fetchall()]

    async def set_scheduled_post_status(self, sched_id: int, status: str) -> None:
        await self._c().execute(
            "UPDATE scheduled_posts SET status=?, sent_at=? WHERE id=?",
            (status, _now(), sched_id),
        )
        await self._c().commit()

    async def cancel_scheduled_post(self, sched_id: int) -> None:
        await self._c().execute(
            "UPDATE scheduled_posts SET status='cancelled' WHERE id=? AND status='pending'",
            (sched_id,),
        )
        await self._c().commit()
