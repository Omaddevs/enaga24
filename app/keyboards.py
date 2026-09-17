from __future__ import annotations

from datetime import date, timedelta

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.texts import ADMIN, ESLATMA_AGREE_BTN, ESLATMA_DISAGREE_BTN, t

CHANNEL_URL = "https://t.me/enaga_1"
VIP_ADMIN_URL = "https://t.me/vip_admin_channels"
BOT_URL = "https://t.me/nyanya_enaga_bot"

# Telegram Bot API inline tugmalarning fon rangini o'zgartirishga imkon bermaydi
# (bu klient temasi bilan boshqariladi), shuning uchun "pink style" pushti
# emoji bilan taqlid qilinadi. Bu yerda barcha InlineKeyboardButton'lar uchun
# markazlashtirilgan, mavjud kodni buzmaydigan integratsiya qilingan.
PINK_MARK = "🩷"


def pinkify(text: str) -> str:
    if not text or text.startswith(PINK_MARK):
        return text
    return f"{PINK_MARK} {text}"


_original_inline_button = InlineKeyboardBuilder.button


def _pink_inline_button(self, *, text: str, **kwargs):
    return _original_inline_button(self, text=pinkify(text), **kwargs)


InlineKeyboardBuilder.button = _pink_inline_button

UZ_WEEKDAYS = ["Dush", "Sesh", "Chor", "Pay", "Juma", "Shan", "Yak"]
UZ_MONTHS = [
    "yanv", "fev", "mart", "apr", "may", "iyun",
    "iyul", "avg", "sen", "okt", "noy", "dek",
]


def lang_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbekcha", callback_data="lang:uz")
    kb.button(text="🇷🇺 Русский", callback_data="lang:ru")
    kb.adjust(2)
    return kb.as_markup()


def home_ikb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "i_nanny"), callback_data="menu:nanny")
    kb.button(text=t(lang, "i_need"), callback_data="menu:need")
    kb.button(text=t(lang, "i_job"), callback_data="menu:job")
    kb.button(text=t(lang, "i_channel"), url=CHANNEL_URL)
    kb.adjust(1)
    return kb.as_markup()


def need_ikb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat in ("elderly_needed", "housekeeper_needed", "worker_needed", "cleaner_needed"):
        kb.button(text=t(lang, f"btn_{cat}"), callback_data=f"cat:{cat}")
    kb.button(text=t(lang, "i_back"), callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def job_ikb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat in ("nanny_job", "elderly_job", "housekeeper_job", "worker_job", "cleaner_job"):
        kb.button(text=t(lang, f"btn_{cat}"), callback_data=f"cat:{cat}")
    kb.button(text=t(lang, "i_back"), callback_data="menu:home")
    kb.adjust(1)
    return kb.as_markup()


def compact_kb(lang: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=t(lang, "btn_home"))
    kb.button(text=t(lang, "btn_my"))
    kb.button(text=t(lang, "btn_lang"))
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)


def wizard_kb(lang: str, *, contact: bool = False, skip: bool = False) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    if contact:
        kb.button(text=t(lang, "btn_share_contact"), request_contact=True)
    if skip:
        kb.button(text=t(lang, "btn_skip"))
    kb.button(text=t(lang, "btn_back"))
    kb.button(text=t(lang, "btn_cancel"))
    kb.adjust(1 if contact else 2, 2)
    return kb.as_markup(resize_keyboard=True)


def preview_kb(lang: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=t(lang, "btn_confirm"))
    kb.button(text=t(lang, "btn_edit"))
    kb.button(text=t(lang, "btn_cancel"))
    kb.adjust(1, 2)
    return kb.as_markup(resize_keyboard=True)


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def admin_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=ADMIN["btn_stats"])
    kb.button(text=ADMIN["btn_pending"])
    kb.button(text=ADMIN["btn_broadcast"])
    kb.button(text=ADMIN["btn_dest"])
    kb.button(text=ADMIN["btn_sub"])
    kb.button(text=ADMIN["btn_views"])
    kb.button(text=ADMIN["btn_admins"])
    kb.button(text=ADMIN["btn_sched"])
    kb.button(text=ADMIN["btn_back_user"])
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def listing_admin_kb(listing_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ADMIN["btn_edit"], callback_data=f"adm:edit:{listing_id}")
    kb.button(text=ADMIN["btn_approve"], callback_data=f"adm:ok:{listing_id}")
    kb.button(text=ADMIN["btn_reject"], callback_data=f"adm:no:{listing_id}")
    kb.adjust(1, 2)
    return kb.as_markup()


def channel_post_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ADMIN["channel_post_btn"], url=BOT_URL)
    kb.adjust(1)
    return kb.as_markup()


def eslatma_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ESLATMA_AGREE_BTN, callback_data="eslatma:agree")
    kb.button(text=ESLATMA_DISAGREE_BTN, callback_data="eslatma:disagree")
    kb.adjust(2)
    return kb.as_markup()


def dest_pick_kb(destinations: list[dict], listing_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for d in destinations:
        kb.button(
            text=ADMIN["dest_post_btn"].format(title=d["title"]),
            callback_data=f"adm:post:{listing_id}:{d['id']}",
        )
    if destinations:
        kb.button(text=ADMIN["btn_all_dest"], callback_data=f"adm:post:{listing_id}:all")
    kb.adjust(1)
    return kb.as_markup()


def dest_manage_kb(items: list[dict], prefix: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for d in items:
        kb.button(text=f"🗑 {d['title']}", callback_data=f"{prefix}:{d['id']}")
    kb.adjust(1)
    return kb.as_markup()


def sub_gate_kb(subs: list[dict], lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for s in subs:
        url = None
        if s.get("username"):
            url = f"https://t.me/{s['username'].lstrip('@')}"
        elif s.get("invite_link"):
            url = s["invite_link"]
        if url:
            kb.button(text=f"📢 {s['title']}", url=url)
        else:
            kb.button(text=f"📢 {s['title']}", callback_data="sub:noop")
    kb.button(text=t(lang, "btn_check_sub"), callback_data="sub:check")
    kb.adjust(1)
    return kb.as_markup()


def bc_target_kb(users: bool, dests: bool) -> InlineKeyboardMarkup:
    u = "✅" if users else "⬜️"
    d = "✅" if dests else "⬜️"
    kb = InlineKeyboardBuilder()
    kb.button(text=f"{u} {ADMIN['bc_users']}", callback_data="bc:tog:users")
    kb.button(text=f"{d} {ADMIN['bc_dest']}", callback_data="bc:tog:dest")
    kb.button(text=ADMIN["bc_next"], callback_data="bc:next")
    kb.adjust(1)
    return kb.as_markup()


def bc_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ADMIN["bc_send"], callback_data="bc:send")
    kb.button(text=ADMIN["bc_cancel"], callback_data="bc:cancel")
    kb.adjust(2)
    return kb.as_markup()


def seen_kb(broadcast_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=pinkify(ADMIN["btn_seen"]), callback_data=f"seen:{broadcast_id}"
                )
            ]
        ]
    )


def sched_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ADMIN["sched_new_btn"], callback_data="schd:new")
    kb.button(text=ADMIN["sched_list_btn"], callback_data="schd:list")
    kb.adjust(1)
    return kb.as_markup()


def sched_dest_kb(destinations: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for d in destinations:
        kb.button(text=f"📡 {d['title']}", callback_data=f"schd:dest:{d['id']}")
    if destinations:
        kb.button(text=ADMIN["dest_all_label"], callback_data="schd:dest:all")
    kb.adjust(1)
    return kb.as_markup()


def sched_date_kb(start: date, days: int = 7) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i in range(days):
        d = start + timedelta(days=i)
        tag = f"{d.day}-{UZ_MONTHS[d.month - 1]}"
        if i == 0:
            label = f"📅 Bugun, {tag}"
        elif i == 1:
            label = f"📅 Ertaga, {tag}"
        else:
            label = f"{tag}, {UZ_WEEKDAYS[d.weekday()]}"
        kb.button(text=label, callback_data=f"schd:date:{d.isoformat()}")
    kb.adjust(2)
    return kb.as_markup()


def sched_hour_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for h in range(1, 25):
        kb.button(text=f"{h:02d}:00", callback_data=f"schd:hour:{h:02d}")
    kb.button(text=ADMIN["btn_sched_back_date"], callback_data="schd:backtodate")
    kb.adjust(4, 4, 4, 4, 4, 4, 1)
    return kb.as_markup()


def sched_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ADMIN["btn_sched_confirm"], callback_data="schd:confirm")
    kb.button(text=ADMIN["btn_sched_edit_content"], callback_data="schd:editcontent")
    kb.button(text=ADMIN["btn_sched_edit_dest"], callback_data="schd:editdest")
    kb.button(text=ADMIN["btn_sched_edit_time"], callback_data="schd:edittime")
    kb.button(text=ADMIN["btn_sched_cancel"], callback_data="schd:cancel")
    kb.adjust(1, 2, 2)
    return kb.as_markup()


def views_kb(posts: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in posts[:15]:
        title = (p.get("dest_title") or str(p["chat_id"]))[:24]
        kb.button(
            text=f"#{p['id']} {title} · {p.get('views') or 0}",
            callback_data=f"views:{p['id']}",
        )
    kb.adjust(1)
    return kb.as_markup()
