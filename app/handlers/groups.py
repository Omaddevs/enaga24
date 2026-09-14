from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message

from app.utils import looks_like_ad

router = Router()


def _is_service(message: Message) -> bool:
    return bool(
        message.new_chat_members
        or message.left_chat_member
        or message.new_chat_title
        or message.new_chat_photo
        or message.delete_chat_photo
        or message.group_chat_created
        or message.supergroup_chat_created
        or message.pinned_message
        or message.forum_topic_created
        or message.forum_topic_closed
        or message.forum_topic_reopened
    )


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def moderate_group(message: Message, bot: Bot) -> None:
    me = await bot.get_chat_member(message.chat.id, bot.id)
    if me.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}:
        return
    if not getattr(me, "can_delete_messages", True):
        return

    if _is_service(message):
        try:
            await message.delete()
        except Exception:
            pass
        return

    user = message.from_user
    if not user:
        return
    member = await bot.get_chat_member(message.chat.id, user.id)
    if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR}:
        return

    if looks_like_ad(message):
        try:
            await message.delete()
        except Exception:
            pass
