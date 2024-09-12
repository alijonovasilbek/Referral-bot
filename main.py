import sqlite3
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import asyncio
from  utils import  commands_admin,commands_user
from aiogram.exceptions import TelegramBadRequest


API_TOKEN = '7255043611:AAEThmAl-OoPP4BL8Ir5UirEpMlHqyN95Co'
CHANNELS = ["@phytonkodlar", "@makhtalks","@usmonovs_learning_center"]


bot = Bot(token=API_TOKEN)
dp = Dispatcher()


logging.basicConfig(level=logging.INFO)
admins=[5737465114,1518725830]


def get_db_connection():
    conn = sqlite3.connect('contest.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    first_name TEXT,
                    username TEXT,
                    referral_count INTEGER DEFAULT 0,
                    is_qualified INTEGER DEFAULT 0,
                    contest_id INTEGER,
                    first_referral_id INTEGER
                   )''')
    return conn



async def check_subscription(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['member', 'administrator', 'creator']:
                return True
        except TelegramBadRequest as e:
            logging.error(f"Error checking subscription for channel {channel}: {e}")
            return False
    return False



@dp.message(Command('start'))
async def send_welcome(message: Message):
    if message.from_user.id in admins:
        await message.bot.set_my_commands(commands=commands_admin)
    await message.bot.set_my_commands(commands=commands_user)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (telegram_id, username,first_name) VALUES (?, ?,?)",
                   (message.from_user.id, message.from_user.username, message.from_user.first_name))
    conn.commit()
    print(message.from_user.username)
    print(message.from_user.first_name)
    args = message.text.split()
    if len(args) > 1:
        referrer_id = int(args[1])
        if referrer_id != message.from_user.id:
            cursor.execute("SELECT is_qualified FROM users WHERE telegram_id = ?", (message.from_user.id,))
            is_qualified = cursor.fetchone()[0]

            if not is_qualified:
                cursor.execute("SELECT referral_count, is_qualified FROM users WHERE telegram_id = ?", (referrer_id,))
                referrer_data = cursor.fetchone()

                if referrer_data:
                    referral_count = referrer_data[0] + 1
                    referrer_qualified = referrer_data[1]

                    if referral_count >= 10 and not referrer_qualified:

                        cursor.execute("SELECT MAX(contest_id) FROM users")
                        max_contest_id = cursor.fetchone()[0]

                        # Agar konkursda hech kim ishtirok etmagan bo'lsa, contest_id 1 bo'ladi, aks holda max_contest_id + 1 bo'ladi
                        contest_id = 1 if max_contest_id is None else max_contest_id + 1

                        # Userga tabriklash xabari va maxsus ID ni yuborish
                        await bot.send_message(referrer_id,
                                               f"""🎉 Tabriklaymiz! 10 ta do‘stingizni muvaffaqiyatli qo‘shdingiz va endi tanlovda rasmiy qatnashuvchisiz!
                                               
🔜 Tanlov natijalari tez orada 
https://t.me/makhtalks kanalida jonli efirda e’lon qilinadi.

Omad siz bilan bo‘lsin! 🍀"""
                                               f"Sizning maxsus konkurs ID raqamingiz: {contest_id}")

                        # Ma'lumotlar bazasida userga ishtirokchi sifatida belgilash
                        cursor.execute("UPDATE users SET is_qualified = 1, contest_id = ? WHERE telegram_id = ?",
                                       (contest_id, referrer_id))

                    cursor.execute("UPDATE users SET referral_count = ? WHERE telegram_id = ?",
                                   (referral_count, referrer_id))
                    conn.commit()
            else:
                await message.answer("Siz konkursda qatnashgansiz va boshqa foydalanuvchilarga ball qo'shilmadi.")
                return

    conn.close()


    is_subscribed = await check_subscription(message.from_user.id)

    if not is_subscribed:

        buttons = [
            InlineKeyboardButton(text="🔥 Makhteach", url=f"https://t.me/{CHANNELS[0][1:]}"),
            InlineKeyboardButton(text="🔥 Piton", url=f"https://t.me/{CHANNELS[1][1:]}"),
            InlineKeyboardButton(text="📚 Usmonovs Learning", url=f"https://t.me/{CHANNELS[2][1:]}"),
            InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data="check_subscription")
        ]

        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
        photo_url = 'https://t.me/phytonkodlar/189'
        await message.answer_photo(
            caption="""USMONOVS' TEAM KANALIDA SUPER TANLOV!

💥 Aziz do'stlar, sizlar uchun ajoyib imkoniyat! Endi Usmonovs' Team kanalimiz orqali maxsus tanlovda ishtirok etishingiz mumkin!
🎯 Ishtirok qilish uchun shartlar juda oddiy:

 1️⃣   10 ta do‘stingizni kanalimizga taklif qiling.
 2️⃣   Bot sizga maxsus ID beradi va https://t.me/makhtalks kanalida jonli chatda g'oliblar aniqlanadi.
 3️⃣   G‘oliblar qimmatbaho sovg‘alar bilan taqdirlanadi!

🔥 Shoshiling, imkoniyatni qo‘ldan boy bermang! Hoziroq 10 ta do‘stingizni taklif qiling va tanlovda ishtirok etish imkoniyatini qo‘lga kiriting!

🎁 G‘olib bo‘ling va yirik sovg‘alarni qo‘lga kiriting!

Quyidagi kanallarga obuna bo'ling.
Keyin ✅'Obuna bo'ldim' tugmasini bosing""",
            photo=photo_url,
            reply_markup=keyboard
        )

    else:
        await send_main_menu(message)



async def send_main_menu(message: Message):
    user_username = message.from_user.username

    greeting = """✨ Tabriklaymiz!

🚀 Maxsus tanlovimizga xush kelibsiz! Bot sizga taqdim etgan maxsus link orqali 10ta do’stingizni loyihamizga taklif qiling va bot sizga avtomatik tarzda loyihada ishtirok etishingiz uchun maxsus ID beradi.

Bu ID orqali https://t.me/makhtalks kanalda jonli efirda g'oliblar aniqlanadi

Sizga taklif posti yuborilgandan so’ng, siz uni do’stlaringizga yuboring va ular botga kirib, to’liq ro’yxatdan o’tsa, sizga +1 ball beriladi.

📲 Bot sizning do‘stlaringizni kuzatadi va ularning qo‘shilishi bilan siz tanlovda qatnashish imkoniyatini qo‘lga kiritasiz!

Shoshiling, imkoniyatni boy bermang! 🎯

Quyidagi tugmani bosing va taklif qilishni boshlang 👇

Ballaringizni ko‘rish uchun "🎗 Ballarim" tugmasini bosing
"""

    buttons = [
        InlineKeyboardButton(text="Taklif posti", callback_data="referral_link"),
        InlineKeyboardButton(text="🎗 Ballarim", callback_data="points")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    photo_url="https://t.me/phytonkodlar/189"
    await message.answer_photo(caption=greeting,photo=photo_url, reply_markup=keyboard)



@dp.callback_query(lambda call: call.data == "check_subscription")
async def handle_check_subscription(call: CallbackQuery):
    is_subscribed = await check_subscription(call.from_user.id)
    if is_subscribed:
        await send_main_menu(call.message)
    else:
        await call.message.answer("Iltimos, avval kanallarga obuna bo'ling!")



@dp.callback_query(lambda call: call.data == "referral_link")
async def handle_referral_link(call: CallbackQuery):
    referral_link = f"https://t.me/makhteach_konkurs_bot?start={call.from_user.id}"
    photo_url = "https://t.me/phytonkodlar/189"

    msg=f"""👋 Do‘stlaringizni Usmonovs' Team kanaliga taklif qiling va tanlovda ishtirok eting!
    
Bu yerda imkoniyatni qo‘lga kiritish uchun siz hamdo‘stlaringizni kanalimizga qo‘shishingiz mumkin:

🔗 Havola ustiga bosing 👇:
{referral_link}

🔥 Eng qizig'i - loyihada ishtirok etish mutlaqo BEPUL. 

📢 Taklif qil, ishtirok et, va yutuqqa erish!

"""


    buttons = [
        InlineKeyboardButton(text="Taklif posti", callback_data="referral_link"),
        InlineKeyboardButton(text="🎗 Ballarim", callback_data="points")
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    await call.message.answer_photo(caption=msg,photo=photo_url,reply_markup=keyboard)



@dp.callback_query(lambda call: call.data == "points")
async def handle_points(call: CallbackQuery):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT referral_count, is_qualified FROM users WHERE telegram_id = ?", (call.from_user.id,))
    result = cursor.fetchone()
    referral_count = result[0] if result else 0
    is_qualified = result[1] if result else 0
    conn.close()

    if is_qualified:
        await call.message.answer(f"""🎉 Tabriklaymiz! 10 ta do‘stingizni muvaffaqiyatli qo‘shdingiz va endi tanlovda rasmiy qatnashuvchisiz!
                                               
🔜 Tanlov natijalari tez orada 
https://t.me/makhtalks kanalida jonli efirda e’lon qilinadi.

Omad siz bilan bo‘lsin! 🍀""")
    else:
        await call.message.answer(f"Sizning ballaringiz: {referral_count}\nYana {10 - referral_count} ball yig'ishingiz kerak.")



async def is_admin(user_id: int):
    admin_ids = [5737465114,1518725830]
    return user_id in admin_ids



@dp.message(Command(commands="contest_list"))
async def send_contest_list(message: Message):
    if await is_admin(message.from_user.id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, contest_id, first_name FROM users WHERE contest_id IS NOT NULL ORDER BY contest_id")
        users = cursor.fetchall()
        conn.close()

        if users:
            response = "Barcha ishtirokchilarning username va maxsus ID raqamlari:\n\n"
            for user in users:
                username = user[0] if user[0] else "Username mavjud emas"
                contest_id = user[1]
                first_name = user[2] if user[2] else "Ism mavjud emas"
                response += f"<b>Name:</b> '{first_name}'   <b>Username:</b> @{username}, <b>ID:</b> {contest_id}\n"
        else:
            response = "Hozircha konkurs ishtirokchilari mavjud emas."

        await message.answer(response, parse_mode="HTML")
    else:
        await message.answer("Bu buyruq faqat adminlar uchun!")



if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))



