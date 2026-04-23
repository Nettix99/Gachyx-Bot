import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# ⚙️ CONFIG
# =========================
ADMIN_ID = 8200958216  # 👈 ЗАМЕНИ НА СВОЙ ID
LOG_CHAT_ID = -1003774664852  # 👈 ID группы логов

# =========================
# 🧠 MEMORY
# =========================
USERS = {}

CARD = {
    "id": 1,
    "name": "Тандзиро Камадо",
    "rarity": "🟡",
    "photo_id": None
}


# =========================
# 👤 USER SYSTEM
# =========================
def get_user(user_id: int):
    if user_id not in USERS:
        USERS[user_id] = {
            "cards": []
        }
    return USERS[user_id]


# =========================
# 💬 START
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    get_user(message.from_user.id)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📁 Профиль"), KeyboardButton(text="🎴 Карта")],
            [KeyboardButton(text="📦 Карты"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

    await message.answer("👋 CardBot запущен", reply_markup=kb)


# =========================
# 🎴 ВЫДАЧА КАРТЫ
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["карта", "🎴 карта"])
async def give_card(message: Message):
    user = get_user(message.from_user.id)

    user["cards"].append(CARD["id"])

    text = (
        f"🎴 Карта получена!\n\n"
        f"🏷 {CARD['name']}\n"
        f"⭐ {CARD['rarity']}"
    )

    if CARD["photo_id"]:
        await message.answer_photo(
            CARD["photo_id"],
            caption=text
        )
    else:
        await message.answer(text)


# =========================
# 📦 ИНВЕНТАРЬ
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["карты", "📦 карты"])
async def inventory(message: Message):
    user = get_user(message.from_user.id)

    await message.answer(f"📦 У тебя {len(user['cards'])} карт(ы)")


# =========================
# 👤 ПРОФИЛЬ
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["профиль", "📁 профиль"])
async def profile(message: Message):
    user = get_user(message.from_user.id)

    await message.answer(
        f"""
👤 Профиль

🆔 ID: {message.from_user.id}

🎴 Карты: {len(user['cards'])}
"""
    )


# =========================
# 🛠 АДМИН
# =========================
@dp.message(lambda m: m.text and m.text.lower() == "админ")
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа")

    await message.answer(
        "🛠 Админ режим\n\n"
        "📸 Отправь фото в чат боту\n"
        "➡ оно станет картой"
    )


# =========================
# 📸 ПРИЁМ ФОТО (АДМИН)
# =========================
@dp.message(F.photo)
async def handle_photo(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    photo = message.photo[-1]
    file_id = photo.file_id

    CARD["photo_id"] = file_id

    # лог в группу
    await bot.send_photo(
        LOG_CHAT_ID,
        photo=file_id,
        caption=(
            f"🖼 Новая карта загружена\n\n"
            f"🎴 {CARD['name']}\n"
            f"⭐ {CARD['rarity']}\n"
            f"🆔 file_id:\n{file_id}"
        )
    )

    await message.answer("✅ Фото сохранено и отправлено в логи")


# =========================
# ❓ HELP
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["помощь", "❓ помощь"])
async def help_cmd(message: Message):
    await message.answer(
        "📖 Команды:\n\n"
        "📁 профиль\n"
        "🎴 карта\n"
        "📦 карты\n"
        "админ"
    )


# =========================
# 🚀 START BOT
# =========================
async def main():
    print("🚀 BOT STARTING...")

    await bot.delete_webhook(drop_pending_updates=True)

    print("🔥 BOT RUNNING")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
