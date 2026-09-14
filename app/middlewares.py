from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from app.db import Database
from app.keyboards import sub_gate_kb
from app.texts import t
from app.utils import is_member


class DbUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        db: Database = data["db"]
        user = data.get("event_from_user")
        if user and not user.is_bot:
            row = await db.upsert_user(
                user.id,
                user.username,
                user.full_name,
            )
            data["lang"] = (row or {}).get("lang") or "uz"
        else:
            data["lang"] = "uz"
        return await handler(event, data)


class SubscriptionMiddleware(BaseMiddleware):
    SKIP_CB = {"lang:", "sub:", "seen:"}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if not user or user.is_bot:
            return await handler(event, data)

        settings = data["settings"]
        db: Database = data["db"]
        if await db.is_admin(user.id, settings.admins):
            return await handler(event, data)

        message: Message | None = event if isinstance(event, Message) else None
        callback: CallbackQuery | None = event if isinstance(event, CallbackQuery) else None

        if message and message.chat.type != "private":
            return await handler(event, data)
        if callback and callback.message and callback.message.chat.type != "private":
            return await handler(event, data)

        if callback and callback.data:
            if any(callback.data.startswith(p) for p in self.SKIP_CB):
                return await handler(event, data)

        if message and message.text and message.text.startswith("/start"):
            return await handler(event, data)

        bot: Bot = data["bot"]
        subs = await db.subscriptions()
        if not subs:
            return await handler(event, data)

        missing = []
        for sub in subs:
            if not await is_member(bot, sub["chat_id"], user.id):
                missing.append(sub)
        if not missing:
            return await handler(event, data)

        lang = data.get("lang") or "uz"
        text = t(lang, "must_sub")
        kb = sub_gate_kb(subs, lang)
        if message:
            await message.answer(text, reply_markup=kb)
        elif callback:
            await callback.answer(t(lang, "sub_no"), show_alert=True)
            await callback.message.answer(text, reply_markup=kb)
        return None
