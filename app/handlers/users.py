from __future__ import annotations

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.db import Database
from app.keyboards import home_ikb, job_ikb, lang_kb, need_ikb, sub_gate_kb
from app.texts import ADMIN, t
from app.utils import is_member

router = Router()
router.message.filter(F.chat.type == "private")


def home_text(lang: str) -> str:
    return f"{t(lang, 'welcome')}\n\n{t(lang, 'welcome_ask')}"


async def show_home(message: Message, lang: str) -> None:
    await message.answer(
        home_text(lang),
        reply_markup=home_ikb(lang),
        disable_web_page_preview=True,
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t("uz", "choose_lang"), reply_markup=lang_kb())


@router.callback_query(F.data.startswith("lang:"))
async def set_lang(call: CallbackQuery, db: Database, state: FSMContext) -> None:
    lang = call.data.split(":")[1]
    await db.set_lang(call.from_user.id, lang)
    await state.clear()
    await call.answer()
    try:
        await call.message.edit_text(
            home_text(lang),
            reply_markup=home_ikb(lang),
            disable_web_page_preview=True,
        )
    except TelegramBadRequest:
        await show_home(call.message, lang)


@router.message(F.text.in_({t("uz", "btn_lang"), t("ru", "btn_lang")}))
@router.message(Command("lang"))
async def change_lang(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t("uz", "choose_lang"), reply_markup=lang_kb())


@router.message(F.text.in_({t("uz", "btn_home"), t("ru", "btn_home")}))
async def home_btn(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await show_home(message, lang)


@router.callback_query(F.data == "menu:home")
async def menu_home(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    try:
        await call.message.edit_text(
            home_text(lang),
            reply_markup=home_ikb(lang),
            disable_web_page_preview=True,
        )
    except TelegramBadRequest:
        await show_home(call.message, lang)


@router.callback_query(F.data == "menu:need")
async def menu_need(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    try:
        await call.message.edit_text(t(lang, "need_title"), reply_markup=need_ikb(lang))
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == "menu:job")
async def menu_job(call: CallbackQuery, lang: str) -> None:
    await call.answer()
    try:
        await call.message.edit_text(t(lang, "job_title"), reply_markup=job_ikb(lang))
    except TelegramBadRequest:
        pass


@router.message(F.text.in_({t("uz", "btn_help"), t("ru", "btn_help")}))
@router.message(Command("help"))
async def help_cmd(message: Message, lang: str) -> None:
    await message.answer(t(lang, "help"), reply_markup=home_ikb(lang))


@router.message(F.text.in_({t("uz", "btn_my"), t("ru", "btn_my")}))
async def my_listings(message: Message, db: Database, lang: str) -> None:
    rows = await db.user_listings(message.from_user.id)
    if not rows:
        await message.answer(t(lang, "no_listings"), reply_markup=home_ikb(lang))
        return
    lines = [t(lang, "my_listings_title")]
    for row in rows:
        st = t(lang, f"status_{row['status']}") if row["status"] in {"pending", "approved", "rejected"} else row["status"]
        cat = t(lang, f"btn_{row['category']}")
        lines.append(f"#{row['id']} · {cat}\n{st}")
    await message.answer("\n\n".join(lines), reply_markup=home_ikb(lang))


@router.callback_query(F.data == "sub:check")
async def check_sub(call: CallbackQuery, db: Database, bot, lang: str) -> None:
    subs = await db.subscriptions()
    if not subs:
        await call.answer(t(lang, "sub_ok"))
        return
    missing = []
    for sub in subs:
        if not await is_member(bot, sub["chat_id"], call.from_user.id):
            missing.append(sub)
    if missing:
        await call.answer(t(lang, "sub_no"), show_alert=True)
        try:
            await call.message.edit_text(t(lang, "must_sub"), reply_markup=sub_gate_kb(subs, lang))
        except TelegramBadRequest:
            pass
        return
    await call.answer(t(lang, "sub_ok"))
    try:
        await call.message.delete()
    except Exception:
        pass
    await show_home(call.message, lang)


@router.callback_query(F.data == "sub:noop")
async def sub_noop(call: CallbackQuery) -> None:
    await call.answer()


@router.callback_query(F.data.startswith("seen:"))
async def seen(call: CallbackQuery, db: Database) -> None:
    bid = int(call.data.split(":")[1])
    n = await db.mark_read(bid, call.from_user.id)
    await call.answer(ADMIN["bc_read"].format(n=n), show_alert=True)
