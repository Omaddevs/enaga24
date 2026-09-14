from __future__ import annotations

from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.db import Database
from app.filters import IsAdmin
from app.keyboards import (
    admin_kb,
    dest_manage_kb,
    sched_confirm_kb,
    sched_date_kb,
    sched_dest_kb,
    sched_hour_kb,
    sched_menu_kb,
)
from app.states import AdminSG
from app.texts import ADMIN, t
from app.utils import (
    TASHKENT_TZ,
    build_content_payload,
    combine_schedule_datetime,
    deliver_content,
    schedule_to_utc_str,
    schedule_utc_str_to_local,
)

router = Router()
router.message.filter(F.chat.type == "private", IsAdmin())
router.callback_query.filter(IsAdmin())


async def _show_preview(bot: Bot, chat_id: int, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(None)
    local_time = schedule_utc_str_to_local(data["sp_at_utc"])
    await deliver_content(bot, chat_id, data["sp_payload"])
    await bot.send_message(
        chat_id,
        ADMIN["sched_preview_caption"].format(dest=data["sp_dest_title"], time=local_time),
        reply_markup=sched_confirm_kb(),
    )


async def _show_date_picker(bot: Bot, chat_id: int) -> None:
    today = datetime.now(TASHKENT_TZ).date()
    await bot.send_message(chat_id, ADMIN["choose_sched_date"], reply_markup=sched_date_kb(today))


async def _show_hour_picker(bot: Bot, chat_id: int) -> None:
    await bot.send_message(chat_id, ADMIN["choose_sched_hour"], reply_markup=sched_hour_kb())


@router.message(F.text == ADMIN["btn_sched"])
async def sched_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(ADMIN["sched_menu"], reply_markup=sched_menu_kb())


@router.callback_query(F.data == "schd:new")
async def sched_new(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminSG.sched_content)
    await state.update_data(
        sp_payload=None,
        sp_dest_id=None,
        sp_dest_title=None,
        sp_dest_chosen=False,
        sp_at_utc=None,
        sp_time_chosen=False,
    )
    await call.answer()
    await call.message.answer(ADMIN["ask_sched_content"])


@router.callback_query(F.data == "schd:list")
async def sched_list(call: CallbackQuery, db: Database) -> None:
    await call.answer()
    items = await db.pending_scheduled_posts()
    if not items:
        await call.message.answer(ADMIN["sched_list_empty"])
        return
    lines = [ADMIN["sched_list_title"], ""]
    kb_items = []
    for row in items:
        local_time = schedule_utc_str_to_local(row["scheduled_at"])
        lines.append(
            ADMIN["sched_list_item"].format(id=row["id"], dest=row["dest_title"], time=local_time)
        )
        kb_items.append({"id": row["id"], "title": f"#{row['id']} {row['dest_title']} — {local_time}"})
    await call.message.answer("\n".join(lines), reply_markup=dest_manage_kb(kb_items, "schddel"))


@router.callback_query(F.data.startswith("schddel:"))
async def sched_delete(call: CallbackQuery, db: Database) -> None:
    sched_id = int(call.data.split(":")[1])
    await db.cancel_scheduled_post(sched_id)
    await call.answer(ADMIN["sched_deleted"])
    try:
        await call.message.edit_text(ADMIN["sched_deleted"])
    except TelegramBadRequest:
        pass


@router.message(AdminSG.sched_content)
async def sched_content(message: Message, state: FSMContext, db: Database, bot: Bot) -> None:
    if message.text in {t("uz", "btn_cancel"), t("ru", "btn_cancel"), ADMIN["btn_back_user"]}:
        await state.clear()
        await message.answer(ADMIN["menu"], reply_markup=admin_kb())
        return
    payload = build_content_payload(message)
    await state.update_data(sp_payload=payload)
    data = await state.get_data()
    if data.get("sp_dest_chosen") and data.get("sp_time_chosen"):
        await _show_preview(bot, message.chat.id, state)
        return
    dests = await db.destinations()
    if not dests:
        await state.clear()
        await message.answer(ADMIN["no_dest"], reply_markup=admin_kb())
        return
    await state.set_state(None)
    await message.answer(ADMIN["choose_sched_dest"], reply_markup=sched_dest_kb(dests))


@router.callback_query(F.data.startswith("schd:dest:"))
async def sched_pick_dest(call: CallbackQuery, state: FSMContext, db: Database, bot: Bot) -> None:
    raw = call.data.split(":")[2]
    if raw == "all":
        dest_id = None
        dest_title = ADMIN["dest_all_label"]
    else:
        dest = await db.get_destination(int(raw))
        if not dest:
            await call.answer("Topilmadi", show_alert=True)
            return
        dest_id = dest["id"]
        dest_title = dest["title"]
    await state.update_data(sp_dest_id=dest_id, sp_dest_title=dest_title, sp_dest_chosen=True)
    data = await state.get_data()
    await call.answer()
    if data.get("sp_time_chosen"):
        await _show_preview(bot, call.message.chat.id, state)
        return
    await _show_date_picker(bot, call.message.chat.id)


@router.callback_query(F.data.startswith("schd:date:"))
async def sched_pick_date(call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    date_iso = call.data.split(":")[2]
    await state.update_data(sp_date=date_iso)
    await call.answer()
    await _show_hour_picker(bot, call.message.chat.id)


@router.callback_query(F.data == "schd:backtodate")
async def sched_back_to_date(call: CallbackQuery, bot: Bot) -> None:
    await call.answer()
    await _show_date_picker(bot, call.message.chat.id)


@router.callback_query(F.data.startswith("schd:hour:"))
async def sched_pick_hour(call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    date_iso = data.get("sp_date")
    if not date_iso:
        await call.answer()
        await _show_date_picker(bot, call.message.chat.id)
        return
    hour = int(call.data.split(":")[2])
    dt = combine_schedule_datetime(date_iso, hour)
    if dt <= datetime.now(TASHKENT_TZ):
        await call.answer(ADMIN["sched_time_past"], show_alert=True)
        return
    await state.update_data(sp_at_utc=schedule_to_utc_str(dt), sp_time_chosen=True)
    await call.answer()
    await _show_preview(bot, call.message.chat.id, state)


@router.callback_query(F.data == "schd:editcontent")
async def sched_edit_content(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminSG.sched_content)
    await call.answer()
    await call.message.answer(ADMIN["ask_sched_content"])


@router.callback_query(F.data == "schd:editdest")
async def sched_edit_dest(call: CallbackQuery, db: Database) -> None:
    dests = await db.destinations()
    if not dests:
        await call.answer(ADMIN["no_dest"], show_alert=True)
        return
    await call.answer()
    await call.message.answer(ADMIN["choose_sched_dest"], reply_markup=sched_dest_kb(dests))


@router.callback_query(F.data == "schd:edittime")
async def sched_edit_time(call: CallbackQuery, bot: Bot) -> None:
    await call.answer()
    await _show_date_picker(bot, call.message.chat.id)


@router.callback_query(F.data == "schd:cancel")
async def sched_cancel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.answer()
    await call.message.answer(ADMIN["sched_cancelled_admin"], reply_markup=admin_kb())


@router.callback_query(F.data == "schd:confirm")
async def sched_confirm(call: CallbackQuery, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    payload = data.get("sp_payload")
    at_utc = data.get("sp_at_utc")
    if not payload or not at_utc:
        await call.answer("Ma'lumot yetarli emas", show_alert=True)
        return
    sched_id = await db.add_scheduled_post(
        admin_id=call.from_user.id,
        content_type=payload["content_type"],
        text=payload.get("text"),
        file_id=payload.get("file_id"),
        from_chat_id=payload.get("from_chat_id"),
        from_message_id=payload.get("from_message_id"),
        dest_id=data.get("sp_dest_id"),
        dest_title=data.get("sp_dest_title") or ADMIN["dest_all_label"],
        scheduled_at=at_utc,
    )
    await state.clear()
    await call.answer()
    local_time = schedule_utc_str_to_local(at_utc)
    await call.message.answer(
        ADMIN["sched_created"].format(id=sched_id, time=local_time), reply_markup=admin_kb()
    )
