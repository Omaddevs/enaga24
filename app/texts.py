from __future__ import annotations

from app.categories import CATEGORY_ORDER

ESLATMA = (
    "⚠️ <b>Эслатма</b>\n\n"
    "Канал маъмурияти иш берувчи ва иш изловчи ўртасидаги келишувлар учун жавобгар эмас.\n\n"
    "📌 Паспорт, пул, қарз, кафиллик, ҳужжатлар ва бошқа келишувлар — томонларнинг шахсий масъулияти.\n\n"
    "📎 Батафсил маълумот PDF файлда."
)

TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык",
        "lang_saved": "Til saqlandi.",
        "welcome": (
            "👋 Bu — Toshkent bo'yicha enagalar va uy xodimlari e'lonlari boti "
            "(<a href=\"https://t.me/enaga_1\">@enaga_1</a> kanali)."
        ),
        "welcome_ask": "<b>Nima qilmoqchisiz?</b>",
        "i_nanny": "👩 Enaga qidirayapman",
        "i_need": "🏠 Parvarishchi / uy ishchisi kerak",
        "i_job": "💼 Ish qidirayapman",
        "i_channel": "📂 Kanaldagi anketalarni ko'rish",
        "i_back": "⬅️ Orqaga",
        "need_title": "Kim kerak? Bo'limni tanlang:",
        "job_title": "Qaysi ishni qidiryapsiz?",
        "btn_home": "🏠 Menyu",
        "help": (
            "<b>Qanday ishlaydi?</b>\n"
            "1) Bo'limni bosing\n"
            "2) Savollarga qisqa javob yozing\n"
            "3) Tayyor e'lonni ko'rib chiqing\n"
            "4) «Tasdiqlash» — adminga yuboriladi\n\n"
            "Admin tasdiqlagach e'lon kanal/guruhga chiqadi.\n"
            "Bekor qilish: «Bekor qilish» tugmasi."
        ),
        "btn_nanny_needed": "🍼 Enaga kerak",
        "btn_nanny_job": "👩‍🍼 Enagalik ishlar",
        "btn_elderly_needed": "🧓 Qariyaga qarovchi kerak",
        "btn_elderly_job": "💚 Qariyalarga g'amxo'rlik",
        "btn_housekeeper_needed": "🏠 Uy xizmatchisi kerak",
        "btn_housekeeper_job": "🧹 Uy xizmatchisi bo'lib ishlash",
        "btn_worker_needed": "👩 Ishchi ayol kerak",
        "btn_worker_job": "💼 Ishchi ayol bo'lib ishlash",
        "btn_cleaner_needed": "✨ Tozalovchi kerak",
        "btn_cleaner_job": "🧽 Tozalovchi bo'lib ishlash",
        "btn_my": "📋 Mening e'lonlarim",
        "btn_lang": "🌐 Til",
        "btn_help": "ℹ️ Yordam",
        "btn_cancel": "❌ Bekor qilish",
        "btn_back": "⬅️ Orqaga",
        "btn_skip": "⏭ O'tkazib yuborish",
        "btn_share_contact": "📱 Telefon raqamni yuborish",
        "btn_confirm": "✅ Tasdiqlash",
        "btn_edit": "✏️ Qayta yozish",
        "cancelled": "Bekor qilindi. Asosiy menyu:",
        "ask_child_age": "👶 Bola yoshini yozing.\nMasalan: <i>8 oy</i> yoki <i>2 yosh</i>",
        "ask_nanny_age": "👩‍🍼 Enaga yoshini yozing.\nMasalan: <i>32 yosh</i>",
        "ask_elder_age": "👵 Qariya yoshini yozing.\nMasalan: <i>78 yosh, yolg'iz</i>",
        "ask_age": "👤 Yoshingizni yozing.\nMasalan: <i>35 yosh</i>",
        "ask_address": "📍 Manzilni yozing.\nMasalan: <i>Toshkent, Chilonzor</i>",
        "ask_work_time": "🕐 Ish vaqtini yozing.\nMasalan: <i>09:00–18:00</i> yoki <i>kuniga 4 soat</i>",
        "ask_salary": "💵 Maosh / xizmat haqini yozing.\nMasalan: <i>2 000 000 so'm</i> yoki <i>kelishiladi</i>",
        "ask_requirements": "📝 Talablarni yozing.\nMasalan: <i>tajriba, tavsiyanoma, doimiy</i>",
        "ask_experience": "🌟 Tajriba va malakalarni yozing.\nMasalan: <i>5 yil, ovqat pishirish, bola parvarishi</i>",
        "ask_contact": (
            "📩 Murojaat uchun telefon yoki username yozing.\n"
            "Yoki pastdagi tugma orqali raqamingizni yuboring."
        ),
        "ask_photo": "🖼 Ixtiyoriy: e'longa rasm yuboring yoki «O'tkazib yuborish»ni bosing.",
        "need_text": "Iltimos, matn yozing yoki tugmalardan foydalaning.",
        "preview_title": "Tayyor e'lon. Tekshirib chiqing:\n\n",
        "preview_hint": "\n\nHammasi to'g'ri bo'lsa — <b>Tasdiqlash</b>.",
        "sent_to_admin": "✅ E'lon adminga yuborildi. Tasdiqlangach kanalga chiqadi.",
        "no_listings": "Hozircha e'loningiz yo'q.",
        "my_listings_title": "<b>Sizning e'lonlaringiz</b>\n",
        "status_pending": "⏳ Kutilmoqda",
        "status_approved": "✅ Tasdiqlangan",
        "status_rejected": "❌ Rad etilgan",
        "must_sub": "Botdan foydalanish uchun avval kanal/guruhga obuna bo'ling:",
        "btn_check_sub": "✅ Obunani tekshirish",
        "sub_ok": "Obuna tasdiqlandi. Davom etishingiz mumkin.",
        "sub_no": "Hali obuna bo'lmadingiz. Iltimos, obuna bo'ling.",
        "subscribe_open": "Obuna bo'lish",
        "approved_user": "✅ E'loningiz tasdiqlandi va joylandi.",
        "rejected_user": "❌ E'loningiz rad etildi.{reason}",
        "reason_prefix": "\nSabab: ",
        "admin_only": "Bu bo'lim faqat admin uchun.",
        "menu_hint": "Asosiy menyu:",
    },
    "ru": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык",
        "lang_saved": "Язык сохранён.",
        "welcome": (
            "👋 Это бот объявлений по няням и домашнему персоналу в Ташкенте "
            "(канал <a href=\"https://t.me/enaga_1\">@enaga_1</a>)."
        ),
        "welcome_ask": "<b>Что вы хотите сделать?</b>",
        "i_nanny": "👩 Ищу няню",
        "i_need": "🏠 Нужен уход / домработница",
        "i_job": "💼 Ищу работу",
        "i_channel": "📂 Смотреть анкеты в канале",
        "i_back": "⬅️ Назад",
        "need_title": "Кто нужен? Выберите раздел:",
        "job_title": "Какую работу ищете?",
        "btn_home": "🏠 Меню",
        "help": (
            "<b>Как это работает?</b>\n"
            "1) Выберите раздел\n"
            "2) Ответьте на вопросы\n"
            "3) Проверьте готовый текст\n"
            "4) «Подтвердить» — отправится админу\n\n"
            "После одобрения пост выйдет в канал/группу.\n"
            "Отмена: кнопка «Отмена»."
        ),
        "btn_nanny_needed": "🍼 Нужна няня",
        "btn_nanny_job": "👩‍🍼 Работа няней",
        "btn_elderly_needed": "🧓 Нужен уход за пожилым",
        "btn_elderly_job": "💚 Уход за пожилыми",
        "btn_housekeeper_needed": "🏠 Нужна домработница",
        "btn_housekeeper_job": "🧹 Работа домработницей",
        "btn_worker_needed": "👩 Нужна работница",
        "btn_worker_job": "💼 Ищу работу работницей",
        "btn_cleaner_needed": "✨ Нужна уборщица",
        "btn_cleaner_job": "🧽 Работа уборщицей",
        "btn_my": "📋 Мои объявления",
        "btn_lang": "🌐 Язык",
        "btn_help": "ℹ️ Помощь",
        "btn_cancel": "❌ Отмена",
        "btn_back": "⬅️ Назад",
        "btn_skip": "⏭ Пропустить",
        "btn_share_contact": "📱 Отправить номер",
        "btn_confirm": "✅ Подтвердить",
        "btn_edit": "✏️ Заполнить заново",
        "cancelled": "Отменено. Главное меню:",
        "ask_child_age": "👶 Укажите возраст ребёнка.\nНапример: <i>8 месяцев</i> или <i>2 года</i>",
        "ask_nanny_age": "👩‍🍼 Укажите возраст няни.\nНапример: <i>32 года</i>",
        "ask_elder_age": "👵 Укажите возраст подопечного.\nНапример: <i>78 лет</i>",
        "ask_age": "👤 Укажите ваш возраст.\nНапример: <i>35 лет</i>",
        "ask_address": "📍 Укажите адрес.\nНапример: <i>Ташкент, Чиланзар</i>",
        "ask_work_time": "🕐 Укажите график.\nНапример: <i>09:00–18:00</i> или <i>4 часа в день</i>",
        "ask_salary": "💵 Укажите оплату.\nНапример: <i>2 000 000 сум</i> или <i>договорная</i>",
        "ask_requirements": "📝 Напишите требования.\nНапример: <i>опыт, рекомендации, постоянно</i>",
        "ask_experience": "🌟 Опыт и навыки.\nНапример: <i>5 лет, готовка, уход за детьми</i>",
        "ask_contact": (
            "📩 Напишите телефон или @username.\n"
            "Или отправьте номер кнопкой ниже."
        ),
        "ask_photo": "🖼 По желанию отправьте фото или нажмите «Пропустить».",
        "need_text": "Напишите текст или используйте кнопки.",
        "preview_title": "Готовое объявление. Проверьте:\n\n",
        "preview_hint": "\n\nЕсли всё верно — нажмите <b>Подтвердить</b>.",
        "sent_to_admin": "✅ Объявление отправлено админу. После одобрения выйдет в канал.",
        "no_listings": "У вас пока нет объявлений.",
        "my_listings_title": "<b>Ваши объявления</b>\n",
        "status_pending": "⏳ На проверке",
        "status_approved": "✅ Одобрено",
        "status_rejected": "❌ Отклонено",
        "must_sub": "Чтобы пользоваться ботом, подпишитесь на канал/группу:",
        "btn_check_sub": "✅ Проверить подписку",
        "sub_ok": "Подписка подтверждена. Можно продолжать.",
        "sub_no": "Подписки ещё нет. Пожалуйста, подпишитесь.",
        "subscribe_open": "Подписаться",
        "approved_user": "✅ Ваше объявление одобрено и опубликовано.",
        "rejected_user": "❌ Ваше объявление отклонено.{reason}",
        "reason_prefix": "\nПричина: ",
        "admin_only": "Этот раздел только для админа.",
        "menu_hint": "Главное меню:",
    },
}

ADMIN = {
    "menu": (
        "<b>Admin panel</b>\n\n"
        "Statistika, e'lonlar, kanallar, majburiy obuna va tarqatma shu yerda."
    ),
    "btn_stats": "📊 Statistika",
    "btn_pending": "📬 Kutilayotgan e'lonlar",
    "btn_broadcast": "📢 Xabar yuborish",
    "btn_dest": "📡 Kanallar / guruhlar",
    "btn_sub": "🔒 Majburiy obuna",
    "btn_views": "👁 Post ko'rishlari",
    "btn_admins": "👤 Adminlar",
    "btn_sched": "🕒 Post vaqti",
    "btn_back_user": "⬅️ Asosiy menyu",
    "admins_list": (
        "<b>Adminlar</b>\n\n"
        "Asosiy admin (.env) o'chirilmaydi. Qo'shimcha adminlarni shu yerdan boshqarasiz."
    ),
    "admins_empty_extra": "Hali qo'shimcha admin yo'q.",
    "admin_env": "🔐 asosiy",
    "admin_extra": "➕ qo'shimcha",
    "ask_admin": (
        "Yangi adminni yuboring:\n"
        "• Telegram ID (masalan <code>123456789</code>)\n"
        "• yoki uning xabarini <b>forward</b> qiling\n"
        "• yoki @username (u botga /start bosgan bo'lishi kerak)\n\n"
        "Bekor: /cancel"
    ),
    "admin_added": "✅ Admin qo'shildi: {who}",
    "admin_already": "Bu foydalanuvchi allaqachon admin.",
    "admin_not_found": "Topilmadi. ID yoki forward yuboring, yoki avval u botga /start bossin.",
    "admin_deleted": "Admin o'chirildi.",
    "admin_cannot_del_env": "Asosiy admin (.env) ni o'chirib bo'lmaydi.",
    "admin_notify": (
        "Siz <b>Enaga24</b> botiga admin qilib qo'shildingiz.\n"
        "Panel: /admin"
    ),
    "no_pending": "Kutilayotgan e'lon yo'q.",
    "listing_card": (
        "<b>E'lon #{id}</b>\n"
        "Bo'lim: {cat}\n"
        "Foydalanuvchi: {user}\n"
        "Holat: {status}\n\n"
        "{body}"
    ),
    "btn_approve": "📢 E'lon berish",
    "btn_reject": "❌ Rad etish",
    "btn_edit": "✏️ Tahrirlash",
    "ask_edit": (
        "E'lon #{id} matnini tahrirlang va yuboring.\n"
        "Rasm ham yuborishingiz mumkin.\n"
        "Bekor: /cancel\n\n"
        "<b>Hozirgi matn:</b>\n{body}"
    ),
    "edited_ok": "E'lon tahrirlandi. Endi «E'lon berish» bilan kanal/guruhga joylashingiz mumkin.",
    "choose_dest": "Qaysi kanal yoki guruhga e'lon berilsin?",
    "btn_all_dest": "📢 Hammaga e'lon berish",
    "dest_post_btn": "📢 {title}",
    "channel_post_btn": "🩷 E'lon berish",
    "posted": "Joylandi: {title}",
    "post_fail": "Xato ({title}): {err}",
    "no_dest": "Avval «Kanallar / guruhlar»ga joylash joyini qo'shing.",
    "ask_reject": "Rad etish sababini yozing yoki «o'tkazib yuborish» deb yozing.",
    "rejected_ok": "E'lon rad etildi.",
    "dest_list": "<b>Joylash joylari</b>\nHar biriga bot admin bo'lishi kerak.",
    "dest_empty": "Hali kanal/guruh yo'q. «Qo'shish»ni bosing.",
    "btn_add_dest": "➕ Joylash joyi qo'shish",
    "btn_del_dest": "🗑 O'chirish",
    "ask_dest": (
        "Kanal yoki guruhni yuboring:\n"
        "• @username\n"
        "• https://t.me/...\n"
        "• yoki chat ID (masalan -100...)\n\n"
        "Bot shu yerda admin bo'lishi shart."
    ),
    "dest_added": "Qo'shildi: {title} (<code>{chat_id}</code>)",
    "dest_fail": "Topilmadi. Botni admin qilib, qayta yuboring.\n{err}",
    "dest_deleted": "O'chirildi.",
    "sub_list": "<b>Majburiy obuna</b>\nUserlar start dan keyin shu yerga obuna bo'lishi shart.",
    "sub_empty": "Majburiy obuna o'chiq.",
    "btn_add_sub": "➕ Obuna qo'shish",
    "btn_del_sub": "🗑 Obunani o'chirish",
    "ask_sub": "Kanal/guruh: @username, link yoki ID. Tekshirish uchun bot admin bo'lsin.",
    "sub_added": "Majburiy obuna: {title}",
    "bc_who": "Kimga yuboriladi?",
    "bc_users": "👥 Bot userlari",
    "bc_dest": "📡 Kanallar/guruhlar",
    "bc_pick": "✅ Belgilash",
    "bc_next": "➡️ Keyingi",
    "bc_content": (
        "Xabarni yuboring: matn, rasm, video yoki boshqa chatdan <b>forward</b>.\n"
        "Bekor: /cancel"
    ),
    "bc_confirm": "Yuborilsinmi?\nQabul qiluvchilar: {n}",
    "bc_send": "🚀 Yuborish",
    "bc_cancel": "❌ Bekor",
    "bc_done": "Tayyor.\nYuborildi: {ok}\nXato: {fail}",
    "bc_read": "👁 O'qildi: {n}",
    "btn_seen": "👁 O'qidim",
    "views_list": "<b>Oxirgi joylangan postlar</b>",
    "views_empty": "Hali joylangan post yo'q.",
    "views_item": "#{id} {title}\n👁 {views}  •  {date}",
    "btn_refresh_views": "🔄 Ko'rishlarni yangilash",
    "sched_menu": (
        "<b>🕒 Rejalashtirilgan postlar</b>\n\n"
        "Kanal yoki guruhga belgilangan vaqtda avtomatik chiqadigan post yarating: "
        "matn, rasm, video yoki fayl — istalgani bo'lishi mumkin."
    ),
    "sched_new_btn": "➕ Yangi rejalashtirilgan post",
    "sched_list_btn": "🗓 Ro'yxat",
    "ask_sched_content": (
        "📝 Yubormoqchi bo'lgan postni yuboring: matn, rasm, video yoki fayl — istalgani.\n"
        "Bekor qilish: /cancel"
    ),
    "choose_sched_dest": "📡 Qaysi kanal yoki guruhga joylansin?",
    "choose_sched_date": "🗓 Sanani tanlang:",
    "choose_sched_hour": "🕒 Soatni tanlang (Toshkent vaqti bo'yicha):",
    "btn_sched_back_date": "⬅️ Sanaga qaytish",
    "sched_time_past": "❗️ Bu vaqt allaqachon o'tib ketgan. Boshqa soat yoki sanani tanlang.",
    "sched_preview_caption": (
        "<b>🕒 Rejalashtirilgan post (oldindan ko'rish)</b>\n\n"
        "📡 Kanal: {dest}\n"
        "🗓 Vaqt: {time} (Toshkent)\n\n"
        "Hammasi to'g'ri bo'lsa — <b>Tasdiqlash</b>."
    ),
    "btn_sched_confirm": "✅ Tasdiqlash",
    "btn_sched_edit_content": "✏️ Postni o'zgartirish",
    "btn_sched_edit_dest": "📡 Kanalni o'zgartirish",
    "btn_sched_edit_time": "🕒 Vaqtni o'zgartirish",
    "btn_sched_cancel": "❌ Bekor qilish",
    "dest_all_label": "📢 Barchasi",
    "sched_created": "✅ Post rejalashtirildi (#{id}).\n🗓 {time} (Toshkent) da avtomatik joylanadi.",
    "sched_cancelled_admin": "Bekor qilindi.",
    "sched_list_title": "<b>🗓 Rejalashtirilgan postlar</b>\nBekor qilish uchun bosing:",
    "sched_list_empty": "Hozircha rejalashtirilgan post yo'q.",
    "sched_list_item": "#{id} {dest} — {time}",
    "sched_deleted": "Rejalashtirilgan post bekor qilindi.",
    "sched_published": "✅ Rejalashtirilgan post #{id} joylandi.\nMuvaffaqiyatli: {ok}  Xato: {fail}",
    "sched_fail_no_dest": "❌ Rejalashtirilgan post #{id} joylanmadi: manzil topilmadi yoki o'chirilgan.",
    "stats": (
        "<b>Statistika</b>\n\n"
        "👥 Foydalanuvchilar: <b>{users}</b>\n"
        "📅 Bugun start: <b>{today}</b>\n\n"
        "📝 E'lonlar: <b>{total}</b>\n"
        "⏳ Kutilmoqda: <b>{pending}</b>\n"
        "✅ Tasdiqlangan: <b>{approved}</b>\n"
        "❌ Rad etilgan: <b>{rejected}</b>\n\n"
        "<b>Bo'limlar</b>\n{by_cat}\n"
        "<b>Joylash joylari</b>\n{by_dest}"
    ),
}


def t(lang: str | None, key: str) -> str:
    pack = TEXTS.get(lang or "uz") or TEXTS["uz"]
    return pack.get(key) or TEXTS["uz"].get(key, key)


def category_button_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for lang in TEXTS:
        for cat in CATEGORY_ORDER:
            mapping[TEXTS[lang][f"btn_{cat}"]] = cat
    return mapping


NAV_KEYS = {
    TEXTS["uz"]["btn_my"],
    TEXTS["ru"]["btn_my"],
    TEXTS["uz"]["btn_lang"],
    TEXTS["ru"]["btn_lang"],
    TEXTS["uz"]["btn_help"],
    TEXTS["ru"]["btn_help"],
    TEXTS["uz"]["btn_cancel"],
    TEXTS["ru"]["btn_cancel"],
    TEXTS["uz"]["btn_home"],
    TEXTS["ru"]["btn_home"],
}
