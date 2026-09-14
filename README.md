# Enaga24 Telegram bot

Enaga, qariyalarga g'amxo'rlik, uy xizmatchisi, ishchi ayol va tozalovchi e'lonlari. Tillar: **o'zbek** va **rus**.

## Ishga tushirish

1. [BotFather](https://t.me/BotFather) dan token oling.
2. O'z Telegram `user_id` ni biling (`@userinfobot`).
3. `.env` yarating:

```
BOT_TOKEN=123456:ABC...
ADMIN_IDS=123456789
DB_PATH=data/enaga24.db
```

Bir nechta admin: `ADMIN_IDS=111,222`

4. O'rnating va ishga tushiring:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

## Admin

Botga `/admin` yuboring.

- **Statistika** — userlar, e'lonlar, bo'limlar, qaysi kanalga nechta joylangan.
- **Kutilayotgan e'lonlar** — tasdiqlash / rad etish. Tasdiqlashdan keyin kanal yoki guruh tanlanadi.
- **Kanallar / guruhlar** — `/add_dest` keyin `@kanal`, link yoki `-100...` ID. Bot o'sha yerda **post yozish** huquqli admin bo'lishi shart.
- **Majburiy obuna** — `/add_sub`. Tekshirish uchun bot kanal/guruhda admin bo'lsin.
- **Xabar yuborish** — userlarga va/yoki kanallarga: matn, rasm, video, fayl yoki forward. Userlarda «O'qidim» tugmasi bor.
- **Adminlar** — qo'shimcha admin qo'shish (`/add_admin`: ID, forward yoki @username). `.env` dagi asosiy admin o'chirilmaydi.
- **Post ko'rishlari** — kanal postlaridagi 👁 ni yangilash (guruhda Telegram views bermaydi).

## Guruh moderatsiyasi

Botni guruhga admin qiling, **xabarlarni o'chirish** huquqini bering. Kirish/chiqish xabarlari va reklama (link, spam so'zlar, kanaldan forward) o'chiriladi. Guruh adminlari tekshirilmaydi.

## Foydalanuvchi oqimi

`/start` → til → bo'lim tugmasi → savollar ketma-ket → oldindan ko'rish → **Tasdiqlash** → adminga. Admin tasdiqlagach tanlangan kanalga chiqadi.
