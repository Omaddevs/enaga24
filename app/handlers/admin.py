from __future__ import annotations

import asyncio

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, MessageOriginHiddenUser, MessageOriginUser

from app.categories import CATEGORY_ORDER
from app.db import Database
from app.filters import IsAdmin
from app.handlers.users import show_home
from app.keyboards import (
    admin_kb,
    bc_confirm_kb,
    bc_target_kb,
    channel_post_kb,
    dest_manage_kb,
    dest_pick_kb,
    listing_admin_kb,
    seen_kb,
    views_kb,
)
from app.states import AdminSG
from app.texts import ADMIN, t
from app.utils import build_content_payload, deliver_content, resolve_chat, user_link
from config import Settings

router = Router()
router.message.filter(F.chat.type == "private", IsAdmin())
router.callback_query.filter(IsAdmin())


def _fmt_stats(data: dict) -> str:
    cat_lines = []
    grouped: dict[str, dict[str, int]] = {}
    for row in data["by_cat"]:
        grouped.setdefault(row["category"], {})[row["status"]] = row["n"]
    for cat in CATEGORY_ORDER:
        info = grouped.get(cat)
        if not info:
            continue
        cat_lines.append(
            f"• {t('uz', f'btn_{cat}')}: "
            f"{info.get('pending', 0)}⏳  {info.get('approved', 0)}✅  {info.get('rejected', 0)}❌"
        )
    dest_lines = []
    for row in data["by_dest"]:
        dest_lines.append(f"• {row['title']}: {row['n']}")
    return ADMIN["stats"].format(
        users=data["users"],
        today=data["today"],
        total=data["total"],
        pending=data["pending"],
        approved=data["approved"],
        rejected=data["rejected"],
        by_cat="\n".join(cat_lines) or "—",
        by_dest="\n".join(dest_lines) or "—",
    )


@router.message(Command("admin"))
@router.message(Command("cancel"))
async def admin_home(message: Message, state: FSMContext) -> None:
    if message.text and message.text.startswith("/cancel"):
        await state.clear()
    await state.clear()
    await message.answer(ADMIN["menu"], reply_markup=admin_kb())


@router.message(F.text == ADMIN["btn_back_user"])
async def back_user(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await show_home(message, lang)


@router.message(F.text == ADMIN["btn_stats"])
async def stats(message: Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    data = await db.stats()
    await message.answer(_fmt_stats(data), reply_markup=admin_kb())


@router.message(F.text == ADMIN["btn_pending"])
async def pending(message: Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    rows = await db.pending_listings()
    if not rows:
        await message.answer(ADMIN["no_pending"], reply_markup=admin_kb())
        return
    for row in rows[:15]:
        await _send_listing_card(message, db, row)


@router.message(F.text == ADMIN["btn_dest"])
async def dest_menu(message: Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    items = await db.destinations(active_only=False)
    text = ADMIN["dest_list"] + "\n\n"
    if not items:
        text += ADMIN["dest_empty"]
    else:
        for d in items:
            uname = f" @{d['username']}" if d.get("username") else ""
            text += f"• {d['title']}{uname}\n<code>{d['chat_id']}</code>\n"
    await message.answer(text, reply_markup=admin_kb())
    await message.answer(
        "Qo'shish: /add_dest\nO'chirish tugmalari:",
        reply_markup=dest_manage_kb(items, "destdel"),
    )


@router.message(Command("add_dest"))
@router.message(F.text == "➕ Joylash joyi qo'shish")
async def add_dest_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminSG.add_dest)
    await message.answer(ADMIN["ask_dest"])


@router.message(AdminSG.add_dest)
async def add_dest_save(message: Message, bot: Bot, db: Database, state: FSMContext) -> None:
    if not message.text:
        await message.answer(ADMIN["ask_dest"])
        return
    if message.text in {t("uz", "btn_cancel"), t("ru", "btn_cancel"), ADMIN["btn_back_user"]}:
        await state.clear()
        await message.answer(ADMIN["menu"], reply_markup=admin_kb())
        return
    try:
        chat = await resolve_chat(bot, message.text)
        await db.add_destination(
            chat.title or getattr(chat, "full_name", None) or str(chat.id),
            chat.id,
            chat.type,
            chat.username,
        )
        await state.clear()
        await message.answer(
            ADMIN["dest_added"].format(title=chat.title or chat.id, chat_id=chat.id),
            reply_markup=admin_kb(),
        )
    except Exception as e:
        await message.answer(ADMIN["dest_fail"].format(err=e), reply_markup=admin_kb())
        await state.clear()


@router.callback_query(F.data.startswith("destdel:"))
async def dest_del(call: CallbackQuery, db: Database) -> None:
    dest_id = int(call.data.split(":")[1])
    await db.delete_destination(dest_id)
    await call.answer(ADMIN["dest_deleted"])
    try:
        await call.message.edit_text(ADMIN["dest_deleted"])
    except TelegramBadRequest:
        pass


@router.message(F.text == ADMIN["btn_sub"])
async def sub_menu(message: Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    items = await db.subscriptions()
    text = ADMIN["sub_list"] + "\n\n"
    if not items:
        text += ADMIN["sub_empty"]
    else:
        for s in items:
            uname = f" @{s['username']}" if s.get("username") else ""
            text += f"• {s['title']}{uname}\n<code>{s['chat_id']}</code>\n"
    await message.answer(text, reply_markup=admin_kb())
    await message.answer("Qo'shish: /add_sub", reply_markup=dest_manage_kb(items, "subdel"))


@router.message(Command("add_sub"))
async def add_sub_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminSG.add_sub)
    await message.answer(ADMIN["ask_sub"])


@router.message(AdminSG.add_sub)
async def add_sub_save(message: Message, bot: Bot, db: Database, state: FSMContext) -> None:
    if not message.text:
        await message.answer(ADMIN["ask_sub"])
        return
    if message.text in {t("uz", "btn_cancel"), t("ru", "btn_cancel"), ADMIN["btn_back_user"]}:
        await state.clear()
        await message.answer(ADMIN["menu"], reply_markup=admin_kb())
        return
    try:
        chat = await resolve_chat(bot, message.text)
        raw = message.text.strip()
        invite = raw if ("t.me/+" in raw or "joinchat" in raw) else chat.invite_link
        await db.add_subscription(
            chat.title or str(chat.id),
            chat.id,
            chat.username,
            invite,
        )
        await state.clear()
        await message.answer(
            ADMIN["sub_added"].format(title=chat.title or chat.id),
            reply_markup=admin_kb(),
        )
    except Exception as e:
        await message.answer(ADMIN["dest_fail"].format(err=e), reply_markup=admin_kb())
        await state.clear()


@router.callback_query(F.data.startswith("subdel:"))
async def sub_del(call: CallbackQuery, db: Database) -> None:
    await db.delete_subscription(int(call.data.split(":")[1]))
    await call.answer(ADMIN["dest_deleted"])
    try:
        await call.message.edit_text(ADMIN["dest_deleted"])
    except TelegramBadRequest:
        pass


async def _send_listing_card(message: Message, db: Database, listing: dict) -> None:
    user = await db.get_user(listing["user_id"])
    card = ADMIN["listing_card"].format(
        id=listing["id"],
        cat=t("uz", f"btn_{listing['category']}"),
        user=user_link(
            listing["user_id"],
            (user or {}).get("username"),
            (user or {}).get("full_name"),
        ),
        status=t("uz", f"status_{listing.get('status') or 'pending'}"),
        body=listing["body"],
    )
    kb = listing_admin_kb(listing["id"])
    if listing.get("photo_id"):
        await message.answer_photo(listing["photo_id"], caption=card[:1024], reply_markup=kb)
    else:
        await message.answer(card, reply_markup=kb)


@router.callback_query(F.data.startswith("adm:edit:"))
async def edit_start(call: CallbackQuery, db: Database, state: FSMContext) -> None:
    listing_id = int(call.data.split(":")[2])
    listing = await db.get_listing(listing_id)
    if not listing or listing["status"] != "pending":
        await call.answer("E'lon topilmadi yoki allaqachon ko'rib chiqilgan", show_alert=True)
        return
    await state.set_state(AdminSG.edit_listing)
    await state.update_data(edit_id=listing_id)
    await call.answer()
    await call.message.answer(ADMIN["ask_edit"].format(id=listing_id, body=listing["body"]))


@router.message(AdminSG.edit_listing)
async def edit_save(message: Message, db: Database, state: FSMContext) -> None:
    if message.text in {t("uz", "btn_cancel"), t("ru", "btn_cancel"), ADMIN["btn_back_user"]}:
        await state.clear()
        await message.answer(ADMIN["menu"], reply_markup=admin_kb())
        return
    data = await state.get_data()
    listing_id = int(data["edit_id"])
    listing = await db.get_listing(listing_id)
    if not listing:
        await state.clear()
        await message.answer("Topilmadi", reply_markup=admin_kb())
        return
    if message.photo:
        body = message.html_text or message.caption or listing["body"]
        await db.update_listing_content(
            listing_id, body, photo_id=message.photo[-1].file_id, update_photo=True
        )
    elif message.text or message.caption:
        body = message.html_text or message.text or message.caption
        await db.update_listing_content(listing_id, body)
    else:
        await message.answer(ADMIN["ask_edit"].format(id=listing_id, body=listing["body"]))
        return
    await state.clear()
    updated = await db.get_listing(listing_id)
    await message.answer(ADMIN["edited_ok"], reply_markup=admin_kb())
    await _send_listing_card(message, db, updated or listing)


@router.callback_query(F.data.startswith("adm:ok:"))
async def approve(call: CallbackQuery, db: Database) -> None:
    listing_id = int(call.data.split(":")[2])
    dests = await db.destinations()
    if not dests:
        await call.answer(ADMIN["no_dest"], show_alert=True)
        return
    await call.answer()
    await call.message.answer(
        ADMIN["choose_dest"],
        reply_markup=dest_pick_kb(dests, listing_id),
    )


@router.callback_query(F.data.startswith("adm:no:"))
async def reject_start(call: CallbackQuery, state: FSMContext) -> None:
    listing_id = int(call.data.split(":")[2])
    await state.set_state(AdminSG.reject_reason)
    await state.update_data(reject_id=listing_id)
    await call.answer()
    await call.message.answer(ADMIN["ask_reject"])


@router.message(AdminSG.reject_reason)
async def reject_save(
    message: Message,
    state: FSMContext,
    db: Database,
    bot: Bot,
    lang: str,
) -> None:
    data = await state.get_data()
    listing_id = int(data["reject_id"])
    reason = (message.text or "").strip()
    if reason.lower() in {"o'tkazib yuborish", "otkazib yuborish", "-", "skip", "пропустить"}:
        reason = None
    listing = await db.get_listing(listing_id)
    if not listing:
        await state.clear()
        await message.answer("Topilmadi", reply_markup=admin_kb())
        return
    await db.set_listing_status(listing_id, "rejected", message.from_user.id, reason)
    await state.clear()
    await message.answer(ADMIN["rejected_ok"], reply_markup=admin_kb())
    user = await db.get_user(listing["user_id"])
    ulang = (user or {}).get("lang") or "uz"
    try:
        await bot.send_message(
            listing["user_id"],
            t(ulang, "rejected_user").format(reason=t(ulang, "reason_prefix") + reason if reason else ""),
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("adm:post:"))
async def post_listing(call: CallbackQuery, db: Database, bot: Bot) -> None:
    _, _, listing_s, dest_s = call.data.split(":")
    listing_id = int(listing_s)
    listing = await db.get_listing(listing_id)
    if not listing:
        await call.answer("Topilmadi", show_alert=True)
        return
    dests = await db.destinations()
    if dest_s == "all":
        targets = dests
    else:
        targets = [d for d in dests if d["id"] == int(dest_s)]
    if not targets:
        await call.answer(ADMIN["no_dest"], show_alert=True)
        return
    await call.answer()
    lines = []
    for dest in targets:
        try:
            if listing.get("photo_id"):
                msg = await bot.send_photo(
                    dest["chat_id"],
                    listing["photo_id"],
                    caption=listing["body"][:1024],
                    reply_markup=channel_post_kb(),
                )
            else:
                msg = await bot.send_message(
                    dest["chat_id"], listing["body"], reply_markup=channel_post_kb()
                )
            views = getattr(msg, "views", None) or 0
            await db.add_post(listing_id, dest["id"], dest["chat_id"], msg.message_id, views)
            lines.append(ADMIN["posted"].format(title=dest["title"]))
        except Exception as e:
            lines.append(ADMIN["post_fail"].format(title=dest["title"], err=e))
    await db.set_listing_status(listing_id, "approved", call.from_user.id)
    await call.message.answer("\n".join(lines), reply_markup=admin_kb())
    user = await db.get_user(listing["user_id"])
    ulang = (user or {}).get("lang") or "uz"
    try:
        await bot.send_message(listing["user_id"], t(ulang, "approved_user"))
    except Exception:
        pass


@router.message(F.text == ADMIN["btn_admins"])
@router.message(Command("add_admin"))
async def admins_menu(message: Message, db: Database, settings: Settings, state: FSMContext) -> None:
    if message.text and message.text.startswith("/add_admin"):
        await state.set_state(AdminSG.add_admin)
        await message.answer(ADMIN["ask_admin"], reply_markup=admin_kb())
        return
    await state.clear()
    extra = await db.extra_admins()
    lines = [ADMIN["admins_list"], ""]
    for uid in settings.admins:
        u = await db.get_user(uid)
        who = user_link(uid, (u or {}).get("username"), (u or {}).get("full_name"))
        lines.append(f"{ADMIN['admin_env']} — {who}")
    removable = [r for r in extra if int(r["user_id"]) not in settings.admins]
    if removable:
        for row in removable:
            who = user_link(row["user_id"], row.get("username"), row.get("full_name"))
            lines.append(f"{ADMIN['admin_extra']} — {who}")
    else:
        lines.append(ADMIN["admins_empty_extra"])
    await message.answer("\n".join(lines), reply_markup=admin_kb())
    items = [
        {
            "id": r["user_id"],
            "title": (r.get("full_name") or r.get("username") or str(r["user_id"])),
        }
        for r in removable
    ]
    await message.answer(
        "Yangi admin: /add_admin\nO'chirish:",
        reply_markup=dest_manage_kb(items, "admdel"),
    )


@router.message(AdminSG.add_admin)
async def add_admin_save(
    message: Message,
    db: Database,
    settings: Settings,
    bot: Bot,
    state: FSMContext,
) -> None:
    if message.text in {t("uz", "btn_cancel"), t("ru", "btn_cancel"), ADMIN["btn_back_user"]}:
        await state.clear()
        await message.answer(ADMIN["menu"], reply_markup=admin_kb())
        return
    found = await _resolve_admin_user(message, db)
    if not found:
        await message.answer(ADMIN["admin_not_found"])
        return
    uid, username, full_name = found
    if await db.is_admin(uid, settings.admins):
        await state.clear()
        await message.answer(ADMIN["admin_already"], reply_markup=admin_kb())
        return
    await db.add_admin(uid, username, full_name, message.from_user.id)
    await state.clear()
    who = user_link(uid, username, full_name)
    await message.answer(ADMIN["admin_added"].format(who=who), reply_markup=admin_kb())
    try:
        await bot.send_message(uid, ADMIN["admin_notify"], reply_markup=admin_kb())
    except Exception:
        pass


@router.callback_query(F.data.startswith("admdel:"))
async def admin_del(call: CallbackQuery, db: Database, settings: Settings) -> None:
    uid = int(call.data.split(":")[1])
    if uid in settings.admins:
        await call.answer(ADMIN["admin_cannot_del_env"], show_alert=True)
        return
    await db.delete_admin(uid)
    await call.answer(ADMIN["admin_deleted"])
    try:
        await call.message.edit_text(ADMIN["admin_deleted"])
    except TelegramBadRequest:
        pass


async def _resolve_admin_user(message: Message, db: Database) -> tuple[int, str | None, str | None] | None:
    origin = message.forward_origin
    if isinstance(origin, MessageOriginUser) and origin.sender_user:
        u = origin.sender_user
        return u.id, u.username, u.full_name
    if isinstance(origin, MessageOriginHiddenUser):
        return None
    if message.contact and message.contact.user_id:
        c = message.contact
        name = " ".join(x for x in [c.first_name, c.last_name] if x)
        return c.user_id, None, name or None
    text = (message.text or "").strip()
    if not text:
        return None
    if text.isdigit():
        uid = int(text)
        row = await db.get_user(uid)
        if row:
            return uid, row.get("username"), row.get("full_name")
        return uid, None, None
    if text.startswith("@") or (len(text) < 40 and " " not in text):
        row = await db.get_user_by_username(text)
        if row:
            return int(row["user_id"]), row.get("username"), row.get("full_name")
    return None


@router.message(F.text == ADMIN["btn_views"])
async def views_menu(message: Message, db: Database, state: FSMContext) -> None:
    await state.clear()
    posts = await db.recent_posts()
    if not posts:
        await message.answer(ADMIN["views_empty"], reply_markup=admin_kb())
        return
    lines = [ADMIN["views_list"], ""]
    for p in posts:
        lines.append(
            ADMIN["views_item"].format(
                id=p["id"],
                title=p.get("dest_title") or p["chat_id"],
                views=p.get("views") or 0,
                date=p["created_at"],
            )
        )
    await message.answer("\n\n".join(lines), reply_markup=views_kb(posts))


@router.callback_query(F.data.startswith("views:"))
async def refresh_views(call: CallbackQuery, db: Database, bot: Bot) -> None:
    post = await db.get_post(int(call.data.split(":")[1]))
    if not post:
        await call.answer("Topilmadi", show_alert=True)
        return
    # Telegram only returns a fresh Message (with `views`) when the edit actually
    # changes something, so alternate the markup instead of always clearing it —
    # otherwise every click after the first hits "message is not modified".
    for markup in (None, channel_post_kb()):
        try:
            msg = await bot.edit_message_reply_markup(
                chat_id=post["chat_id"],
                message_id=post["message_id"],
                reply_markup=markup,
            )
        except TelegramBadRequest as e:
            if "not modified" in str(e).lower():
                continue
            await call.answer(str(e)[:180], show_alert=True)
            return
        else:
            views = getattr(msg, "views", None) or 0
            await db.set_post_views(post["id"], views)
            await call.answer(f"👁 {views}")
            return
    await call.answer("Yangilanmadi", show_alert=True)


@router.message(F.text == ADMIN["btn_broadcast"])
async def bc_start(message: Message, state: FSMContext) -> None:
    await state.set_state(None)
    await state.update_data(bc_users=True, bc_dest=False, bc_payload=None)
    await message.answer(ADMIN["bc_who"], reply_markup=bc_target_kb(True, False))


@router.callback_query(F.data.startswith("bc:tog:"))
async def bc_toggle(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    users = bool(data.get("bc_users", True))
    dests = bool(data.get("bc_dest", False))
    if call.data.endswith("users"):
        users = not users
    else:
        dests = not dests
    await state.update_data(bc_users=users, bc_dest=dests)
    await call.answer()
    try:
        await call.message.edit_reply_markup(reply_markup=bc_target_kb(users, dests))
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "bc:next")
async def bc_next(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if not data.get("bc_users") and not data.get("bc_dest"):
        await call.answer("Kamida bitta yo'nalish tanlang", show_alert=True)
        return
    await state.set_state(AdminSG.bc_content)
    await call.answer()
    await call.message.answer(ADMIN["bc_content"])


@router.message(AdminSG.bc_content)
async def bc_content(message: Message, state: FSMContext, db: Database) -> None:
    payload = build_content_payload(message)

    data = await state.get_data()
    n = 0
    if data.get("bc_users"):
        n += len(await db.user_ids())
    if data.get("bc_dest"):
        n += len(await db.destinations())
    await state.update_data(bc_payload=payload)
    await state.set_state(AdminSG.bc_confirm)
    await message.answer(ADMIN["bc_confirm"].format(n=n), reply_markup=bc_confirm_kb())


@router.callback_query(F.data == "bc:cancel")
async def bc_cancel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.answer()
    await call.message.answer(ADMIN["menu"], reply_markup=admin_kb())


@router.callback_query(F.data == "bc:send")
async def bc_send(call: CallbackQuery, state: FSMContext, db: Database, bot: Bot) -> None:
    data = await state.get_data()
    payload = data.get("bc_payload")
    if not payload:
        await call.answer("Xabar yo'q", show_alert=True)
        return
    await call.answer("Yuborilmoqda...")
    bid = await db.add_broadcast(call.from_user.id, "mixed", payload)
    ok = fail = 0
    targets: list[tuple[str, int]] = []
    if data.get("bc_users"):
        for uid in await db.user_ids():
            targets.append(("user", uid))
    if data.get("bc_dest"):
        for d in await db.destinations():
            targets.append(("dest", d["chat_id"]))

    for kind, chat_id in targets:
        try:
            kb = seen_kb(bid, "uz") if kind == "user" else None
            await deliver_content(bot, chat_id, payload, kb)
            ok += 1
        except (TelegramBadRequest, TelegramForbiddenError):
            fail += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)
    await db.finish_broadcast(bid, ok, fail)
    await state.clear()
    await call.message.answer(ADMIN["bc_done"].format(ok=ok, fail=fail), reply_markup=admin_kb())
