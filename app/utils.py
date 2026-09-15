from __future__ import annotations

import html
import re
from datetime import datetime, timedelta, timezone
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Chat, InlineKeyboardMarkup, Message, User

from app.categories import CATEGORIES
from app.texts import t

TASHKENT_TZ = timezone(timedelta(hours=5))


def h(value: Any) -> str:
    return html.escape(str(value or "").strip(), quote=False)


def split_caption(text: str, limit: int = 1024) -> tuple[str, str | None]:
    """Return (caption, overflow) so a photo caption never gets cut mid-HTML-tag.

    Slicing an HTML string by raw character count can land inside a tag
    (e.g. "<b>") and Telegram then rejects the whole request with
    "can't parse entities". If it doesn't fit, send no caption and let the
    caller follow up with the full text as a separate message instead.
    """
    if len(text) <= limit:
        return text, None
    return "", text


def display_name(user: User) -> str:
    return user.full_name or user.username or str(user.id)


def user_link(user_id: int, username: str | None, full_name: str | None) -> str:
    if username:
        return f"@{h(username)} (<code>{user_id}</code>)"
    name = h(full_name or user_id)
    return f'<a href="tg://user?id={user_id}">{name}</a> (<code>{user_id}</code>)'


def render_listing(category: str, answers: dict[str, str], lang: str) -> str:
    spec = CATEGORIES[category]
    template = spec["template_ru"] if lang == "ru" else spec["template"]
    safe = {k: h(v) for k, v in answers.items() if k != "photo"}
    try:
        return template.format(**safe)
    except KeyError:
        return template


def field_prompt(lang: str, field_key: str) -> str:
    return t(lang, f"ask_{field_key}")


async def resolve_chat(bot: Bot, raw: str) -> Chat:
    text = raw.strip()
    target: str | int
    if "t.me/" in text:
        part = text.split("t.me/", 1)[1].split("?")[0].strip("/")
        if part.startswith("+") or part.startswith("joinchat/"):
            target = text if text.startswith("http") else f"https://t.me/{part}"
        else:
            target = "@" + part.replace("@", "")
    elif text.startswith("@"):
        target = text
    elif re.fullmatch(r"-?\d+", text):
        target = int(text)
    else:
        target = text
    chat = await bot.get_chat(target)
    return chat


def chat_url(chat: Chat | dict[str, Any]) -> str | None:
    if isinstance(chat, dict):
        username = chat.get("username")
        invite = chat.get("invite_link")
        chat_id = chat.get("chat_id")
    else:
        username = chat.username
        invite = chat.invite_link
        chat_id = chat.id
    if username:
        return f"https://t.me/{username}"
    if invite:
        return invite
    if chat_id and str(chat_id).startswith("-100"):
        internal = str(chat_id)[4:]
        return f"https://t.me/c/{internal}"
    return None


async def is_member(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except TelegramBadRequest:
        return False
    return member.status in {"creator", "administrator", "member", "restricted"}


def looks_like_ad(message: Message) -> bool:
    text = (message.text or message.caption or "").lower()
    if message.forward_from_chat and message.forward_from_chat.type in {"channel", "supergroup"}:
        return True
    if re.search(r"(t\.me/|telegram\.me/|https?://|instagram\.com|wa\.me/)", text, re.I):
        return True
    if re.search(
        r"(reklama|реклама|casino|казино|crypto|krypto|binance|sotiladi|продаю|stavka|ставки)",
        text,
        re.I,
    ):
        return True
    entities = message.entities or message.caption_entities or []
    return any(e.type in {"url", "text_link"} for e in entities)


def build_content_payload(message: Message) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "content_type": message.content_type,
        "text": message.html_text or message.text or message.caption,
        "file_id": None,
        "from_chat_id": message.chat.id,
        "from_message_id": message.message_id,
    }
    if message.photo:
        payload["file_id"] = message.photo[-1].file_id
        payload["content_type"] = "photo"
    elif message.video:
        payload["file_id"] = message.video.file_id
        payload["content_type"] = "video"
    elif message.document:
        payload["file_id"] = message.document.file_id
        payload["content_type"] = "document"
    elif message.animation:
        payload["file_id"] = message.animation.file_id
        payload["content_type"] = "animation"
    elif message.voice:
        payload["file_id"] = message.voice.file_id
        payload["content_type"] = "voice"
    elif message.video_note:
        payload["file_id"] = message.video_note.file_id
        payload["content_type"] = "video_note"
    elif message.text:
        payload["content_type"] = "text"
    else:
        payload["content_type"] = "copy"
    return payload


async def deliver_content(
    bot: Bot,
    chat_id: int,
    payload: dict[str, Any],
    kb: InlineKeyboardMarkup | None = None,
) -> None:
    ctype = payload.get("content_type")
    text = payload.get("text")
    file_id = payload.get("file_id")
    if ctype == "text":
        await bot.send_message(chat_id, text or "", reply_markup=kb)
        return
    if ctype == "photo" and file_id:
        await bot.send_photo(chat_id, file_id, caption=text, reply_markup=kb)
        return
    if ctype == "video" and file_id:
        await bot.send_video(chat_id, file_id, caption=text, reply_markup=kb)
        return
    if ctype == "document" and file_id:
        await bot.send_document(chat_id, file_id, caption=text, reply_markup=kb)
        return
    if ctype == "animation" and file_id:
        await bot.send_animation(chat_id, file_id, caption=text, reply_markup=kb)
        return
    if ctype == "voice" and file_id:
        await bot.send_voice(chat_id, file_id, caption=text, reply_markup=kb)
        return
    if ctype == "video_note" and file_id:
        await bot.send_video_note(chat_id, file_id)
        if kb:
            await bot.send_message(chat_id, "👆", reply_markup=kb)
        return
    await bot.copy_message(
        chat_id,
        payload["from_chat_id"],
        payload["from_message_id"],
        reply_markup=kb,
    )


def combine_schedule_datetime(date_iso: str, hour: int) -> datetime:
    d = datetime.strptime(date_iso, "%Y-%m-%d")
    if hour >= 24:
        d += timedelta(days=1)
        hour -= 24
    return d.replace(hour=hour, minute=0, second=0, tzinfo=TASHKENT_TZ)


def schedule_to_utc_str(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def schedule_utc_str_to_local(value: str) -> str:
    dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return dt.astimezone(TASHKENT_TZ).strftime("%Y-%m-%d %H:%M")
