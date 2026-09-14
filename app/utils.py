from __future__ import annotations

import html
import re
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Chat, Message, User

from app.categories import CATEGORIES
from app.texts import t


def h(value: Any) -> str:
    return html.escape(str(value or "").strip(), quote=False)


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
