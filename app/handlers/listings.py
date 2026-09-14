from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.categories import CATEGORIES
from app.db import Database
from app.handlers.users import show_home
from app.keyboards import listing_admin_kb, preview_kb, wizard_kb
from app.states import ListingSG
from app.texts import ADMIN, category_button_map, t
from app.utils import field_prompt, render_listing, user_link
from config import Settings

router = Router()
router.message.filter(F.chat.type == "private")

CAT_MAP = category_button_map()


def _field(category: str, step: int) -> dict:
    return CATEGORIES[category]["fields"][step]


async def _ask(message: Message, lang: str, category: str, step: int) -> None:
    field = _field(category, step)
    skip = field["type"] == "photo_optional"
    contact = field["type"] == "contact"
    await message.answer(
        field_prompt(lang, field["key"]),
        reply_markup=wizard_kb(lang, contact=contact, skip=skip),
    )


@router.callback_query(F.data == "menu:nanny")
async def menu_nanny(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await call.answer()
    await _start(call.message, state, lang, "nanny_needed")


@router.callback_query(F.data.startswith("cat:"))
async def start_listing_cb(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    category = call.data.split(":", 1)[1]
    if category not in CATEGORIES:
        await call.answer()
        return
    await call.answer()
    await _start(call.message, state, lang, category)


@router.message(F.text.in_(set(CAT_MAP)))
async def start_listing(message: Message, state: FSMContext, lang: str) -> None:
    await _start(message, state, lang, CAT_MAP[message.text])


async def _start(message: Message, state: FSMContext, lang: str, category: str) -> None:
    await state.set_state(ListingSG.filling)
    await state.set_data({"category": category, "answers": {}, "step": 0, "photo_id": None})
    await _ask(message, lang, category, 0)


@router.message(ListingSG.filling, F.text.in_({t("uz", "btn_cancel"), t("ru", "btn_cancel")}))
@router.message(ListingSG.preview, F.text.in_({t("uz", "btn_cancel"), t("ru", "btn_cancel")}))
async def cancel_listing(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await show_home(message, lang)


@router.message(ListingSG.preview, F.text.in_({t("uz", "btn_edit"), t("ru", "btn_edit")}))
async def restart_listing(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    category = data["category"]
    await state.set_state(ListingSG.filling)
    await state.update_data(answers={}, step=0, photo_id=None)
    await _ask(message, lang, category, 0)


@router.message(ListingSG.filling, F.text.in_({t("uz", "btn_back"), t("ru", "btn_back")}))
async def back_step(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    step = int(data.get("step") or 0)
    if step <= 0:
        await state.clear()
        await show_home(message, lang)
        return
    step -= 1
    answers = dict(data.get("answers") or {})
    field = _field(data["category"], step)
    answers.pop(field["key"], None)
    if field["key"] == "photo":
        await state.update_data(photo_id=None)
    await state.update_data(step=step, answers=answers)
    await _ask(message, lang, data["category"], step)


@router.message(ListingSG.filling)
async def fill_step(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    category = data["category"]
    step = int(data["step"])
    field = _field(category, step)
    answers = dict(data.get("answers") or {})
    skip_texts = {t("uz", "btn_skip"), t("ru", "btn_skip")}

    if field["type"] == "photo_optional":
        if message.photo:
            await state.update_data(photo_id=message.photo[-1].file_id)
        elif message.text in skip_texts:
            await state.update_data(photo_id=None)
        else:
            await message.answer(t(lang, "ask_photo"), reply_markup=wizard_kb(lang, skip=True))
            return
    elif field["type"] == "contact":
        if message.contact and message.contact.phone_number:
            answers[field["key"]] = message.contact.phone_number
        elif message.text and message.text not in skip_texts | {t("uz", "btn_back"), t("ru", "btn_back")}:
            answers[field["key"]] = message.text.strip()
        else:
            await message.answer(t(lang, "need_text"))
            return
    else:
        if not message.text:
            await message.answer(t(lang, "need_text"))
            return
        if message.text in skip_texts:
            await message.answer(t(lang, "need_text"))
            return
        answers[field["key"]] = message.text.strip()

    fields = CATEGORIES[category]["fields"]
    step += 1
    await state.update_data(answers=answers, step=step)

    if step >= len(fields):
        body = render_listing(category, answers, lang)
        await state.set_state(ListingSG.preview)
        photo_id = (await state.get_data()).get("photo_id")
        text = t(lang, "preview_title") + body + t(lang, "preview_hint")
        if photo_id:
            await message.answer_photo(photo_id, caption=text[:1024], reply_markup=preview_kb(lang))
        else:
            await message.answer(text, reply_markup=preview_kb(lang))
        return

    await _ask(message, lang, category, step)


@router.message(ListingSG.preview, F.text.in_({t("uz", "btn_confirm"), t("ru", "btn_confirm")}))
async def confirm_listing(
    message: Message,
    state: FSMContext,
    db: Database,
    bot: Bot,
    settings: Settings,
    lang: str,
) -> None:
    data = await state.get_data()
    category = data["category"]
    answers = data.get("answers") or {}
    photo_id = data.get("photo_id")
    body = render_listing(category, answers, lang)
    listing_id = await db.add_listing(
        message.from_user.id,
        category,
        answers,
        body,
        photo_id,
    )
    await state.clear()
    await message.answer(t(lang, "sent_to_admin"))
    await show_home(message, lang)

    user = message.from_user
    card = ADMIN["listing_card"].format(
        id=listing_id,
        cat=t(lang, f"btn_{category}"),
        user=user_link(user.id, user.username, user.full_name),
        status=t(lang, "status_pending"),
        body=body,
    )
    kb = listing_admin_kb(listing_id)
    for admin_id in await db.all_admin_ids(settings.admins):
        try:
            if photo_id:
                await bot.send_photo(admin_id, photo_id, caption=card[:1024], reply_markup=kb)
            else:
                await bot.send_message(admin_id, card, reply_markup=kb)
        except Exception:
            continue


@router.message(ListingSG.preview)
async def preview_other(message: Message, lang: str) -> None:
    await message.answer(t(lang, "preview_hint").strip(), reply_markup=preview_kb(lang))
