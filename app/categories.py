from __future__ import annotations

from typing import Any

Field = dict[str, Any]

# field types: text | contact | photo_optional
CATEGORIES: dict[str, dict[str, Any]] = {
    "nanny_needed": {
        "kind": "need",
        "fields": [
            {"key": "child_age", "type": "text"},
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "requirements", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "🍼 <b>Enaga kerak!</b>\n\n"
            "👶 Bola yoshi: {child_age}\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Maosh: {salary}\n"
            "Talablar: {requirements}\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "🍼 <b>Нужна няня!</b>\n\n"
            "👶 Возраст ребёнка: {child_age}\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Зарплата: {salary}\n"
            "Требования: {requirements}\n"
            "📩 Связь: {contact}"
        ),
    },
    "nanny_job": {
        "kind": "offer",
        "fields": [
            {"key": "nanny_age", "type": "text"},
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "experience", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "🍼 <b>Enaga xizmati bor</b>\n\n"
            "👩‍🍼 Enaga yoshi: {nanny_age}\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Xizmat haqi: {salary}\n\n"
            "<b>Tajriba va malakalar:</b> {experience}\n\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "🍼 <b>Предлагаю услуги няни</b>\n\n"
            "👩‍🍼 Возраст няни: {nanny_age}\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Оплата: {salary}\n\n"
            "<b>Опыт и навыки:</b> {experience}\n\n"
            "📩 Связь: {contact}"
        ),
    },
    "elderly_needed": {
        "kind": "need",
        "fields": [
            {"key": "elder_age", "type": "text"},
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "requirements", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "🧓 <b>Qariyaga qarovchi kerak!</b>\n\n"
            "👵 Yoshi: {elder_age}\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Maosh: {salary}\n"
            "Talablar: {requirements}\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "🧓 <b>Нужен уход за пожилым!</b>\n\n"
            "👵 Возраст: {elder_age}\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Зарплата: {salary}\n"
            "Требования: {requirements}\n"
            "📩 Связь: {contact}"
        ),
    },
    "elderly_job": {
        "kind": "offer",
        "fields": [
            {"key": "age", "type": "text"},
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "experience", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "🧓 <b>Qariyalarga g'amxo'rlik qilaman</b>\n\n"
            "👤 Yoshi: {age}\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Xizmat haqi: {salary}\n\n"
            "<b>Tajriba:</b> {experience}\n\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "🧓 <b>Ухаживаю за пожилыми</b>\n\n"
            "👤 Возраст: {age}\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Оплата: {salary}\n\n"
            "<b>Опыт:</b> {experience}\n\n"
            "📩 Связь: {contact}"
        ),
    },
    "housekeeper_needed": {
        "kind": "need",
        "fields": [
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "requirements", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "🏠 <b>Uy xizmatchisi kerak!</b>\n\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Maosh: {salary}\n"
            "Talablar: {requirements}\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "🏠 <b>Нужна домработница!</b>\n\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Зарплата: {salary}\n"
            "Требования: {requirements}\n"
            "📩 Связь: {contact}"
        ),
    },
    "housekeeper_job": {
        "kind": "offer",
        "fields": [
            {"key": "age", "type": "text"},
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "experience", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "🏠 <b>Uy xizmatchisi bo'lib ishlayman</b>\n\n"
            "👤 Yoshi: {age}\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Xizmat haqi: {salary}\n\n"
            "<b>Tajriba:</b> {experience}\n\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "🏠 <b>Работаю домработницей</b>\n\n"
            "👤 Возраст: {age}\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Оплата: {salary}\n\n"
            "<b>Опыт:</b> {experience}\n\n"
            "📩 Связь: {contact}"
        ),
    },
    "worker_needed": {
        "kind": "need",
        "fields": [
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "requirements", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "👩 <b>Ishchi ayol kerak!</b>\n\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Maosh: {salary}\n"
            "Talablar: {requirements}\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "👩 <b>Нужна работница!</b>\n\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Зарплата: {salary}\n"
            "Требования: {requirements}\n"
            "📩 Связь: {contact}"
        ),
    },
    "worker_job": {
        "kind": "offer",
        "fields": [
            {"key": "age", "type": "text"},
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "experience", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "👩 <b>Ishchi ayol bo'lib ishlayman</b>\n\n"
            "👤 Yoshi: {age}\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Xizmat haqi: {salary}\n\n"
            "<b>Tajriba:</b> {experience}\n\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "👩 <b>Ищу работу работницей</b>\n\n"
            "👤 Возраст: {age}\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Оплата: {salary}\n\n"
            "<b>Опыт:</b> {experience}\n\n"
            "📩 Связь: {contact}"
        ),
    },
    "cleaner_needed": {
        "kind": "need",
        "fields": [
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "requirements", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "🧹 <b>Tozalovchi kerak!</b>\n\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Maosh: {salary}\n"
            "Talablar: {requirements}\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "🧹 <b>Нужна уборщица!</b>\n\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Зарплата: {salary}\n"
            "Требования: {requirements}\n"
            "📩 Связь: {contact}"
        ),
    },
    "cleaner_job": {
        "kind": "offer",
        "fields": [
            {"key": "age", "type": "text"},
            {"key": "address", "type": "text"},
            {"key": "work_time", "type": "text"},
            {"key": "salary", "type": "text"},
            {"key": "experience", "type": "text"},
            {"key": "contact", "type": "contact"},
            {"key": "photo", "type": "photo_optional"},
        ],
        "template": (
            "🧹 <b>Tozalovchi bo'lib ishlayman</b>\n\n"
            "👤 Yoshi: {age}\n"
            "📍 Manzil: {address}\n"
            "🕐 Ish vaqti: {work_time}\n"
            "💵 Xizmat haqi: {salary}\n\n"
            "<b>Tajriba:</b> {experience}\n\n"
            "📩 Murojaat uchun: {contact}"
        ),
        "template_ru": (
            "🧹 <b>Работаю уборщицей</b>\n\n"
            "👤 Возраст: {age}\n"
            "📍 Адрес: {address}\n"
            "🕐 График: {work_time}\n"
            "💵 Оплата: {salary}\n\n"
            "<b>Опыт:</b> {experience}\n\n"
            "📩 Связь: {contact}"
        ),
    },
}

CATEGORY_ORDER = [
    "nanny_needed",
    "nanny_job",
    "elderly_needed",
    "elderly_job",
    "housekeeper_needed",
    "housekeeper_job",
    "worker_needed",
    "worker_job",
    "cleaner_needed",
    "cleaner_job",
]
