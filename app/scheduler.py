from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot

from app.db import Database
from app.keyboards import channel_post_kb
from app.texts import ADMIN
from app.utils import deliver_content

logger = logging.getLogger("enaga24.scheduler")

CHECK_INTERVAL = 20


async def run_scheduled_posts(bot: Bot, db: Database) -> None:
    while True:
        try:
            await _tick(bot, db)
        except Exception:
            logger.exception("Scheduled post tick failed")
        await asyncio.sleep(CHECK_INTERVAL)


async def _tick(bot: Bot, db: Database) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    for row in await db.due_scheduled_posts(now):
        await _publish(bot, db, row)


async def _publish(bot: Bot, db: Database, row: dict) -> None:
    payload = {
        "content_type": row["content_type"],
        "text": row["text"],
        "file_id": row["file_id"],
        "from_chat_id": row["from_chat_id"],
        "from_message_id": row["from_message_id"],
    }
    if row["dest_id"] is None:
        targets = await db.destinations()
    else:
        dest = await db.get_destination(row["dest_id"])
        targets = [dest] if dest else []

    if not targets:
        await db.set_scheduled_post_status(row["id"], "failed")
        await _notify_admin(bot, row["admin_id"], ADMIN["sched_fail_no_dest"].format(id=row["id"]))
        return

    ok = fail = 0
    for dest in targets:
        try:
            await deliver_content(bot, dest["chat_id"], payload, channel_post_kb())
            ok += 1
        except Exception:
            logger.exception("Failed to publish scheduled post #%s to %s", row["id"], dest["chat_id"])
            fail += 1

    await db.set_scheduled_post_status(row["id"], "sent" if ok else "failed")
    await _notify_admin(
        bot,
        row["admin_id"],
        ADMIN["sched_published"].format(id=row["id"], ok=ok, fail=fail),
    )


async def _notify_admin(bot: Bot, admin_id: int, text: str) -> None:
    try:
        await bot.send_message(admin_id, text)
    except Exception:
        pass
