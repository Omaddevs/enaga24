from __future__ import annotations

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.db import Database
from config import Settings


class IsAdmin(BaseFilter):
    async def __call__(
        self,
        event: Message | CallbackQuery,
        settings: Settings,
        db: Database,
    ) -> bool:
        user = event.from_user
        if not user:
            return False
        return await db.is_admin(user.id, settings.admins)
