import asyncio
import logging
import random

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# 🧠 MEMORY STORAGE
# =========================
USERS = {}

CARDS = [
    {"name": "Саконжи Урокодаки", "rarity": "⚪"},
    {"name": "Мурата", "rarity": "⚪"},
    {"name": "Аои Канзаки", "rarity": "⚪"},
    {"name": "Канао Цуюри", "rarity": "🟢"},
    {"name": "Генъя Шинадзугава", "rarity": "🟢"},
    {"name": "Тамайо", "rarity": "🟢"},
    {"name": "Юширо", "rarity": "🟢"},
    {"name": "Зеницу Агацума", "rarity": "🔵"},
    {"name": "Иноске Хашибира", "rarity": "🔵"},
    {"name": "Синобу Кочо", "rarity": "🔵"},
    {"name": "Гию Томиока", "rarity": "🔵"},
    {"name": "Кёджуро Ренгоку", "rarity": "🟣"},
    {"name": "Тэнген Узуи", "rarity": "🟣"},
    {"name": "Музан Кибуцуджи", "rarity": "🟣"},
    {"name": "Тандзиро Камадо", "rarity": "🟡"},
]


# =========================
# 👤 USER SYSTEM
# =========================
def get_user(user_id: int):
    if user_id not in USERS:
        USERS[user_id] = {
            "balance": 0,
            "cards": [],
            "fragments": 0,
            "tree": 120,
            "active": None
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

    await message.answer("👋 Добро пожаловать в CardBot!", reply_markup=kb)


# =========================
# 🎴 ВЫДАЧА КАРТЫ
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["карта", "🎴 карта"])
async def card(message: Message):
    user = get_user(message.from_user.id)

    card = random.choice(CARDS)
    user["cards"].append(card)

    await message.answer(
        f"🎴 Ты получил карту!\n\n"
        f"🏷 {card['name']}\n"
        f"⭐ {card['rarity']}"
    )


# =========================
# 📦 ИНВЕНТАРЬ
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["карты", "📦 карты"])
async def inventory(message: Message):
    user = get_user(message.from_user.id)

    if not user["cards"]:
        await message.answer("📦 У тебя нет карт")
        return

    text = "📦 Твои карты:\n\n"

    for c in user["cards"][-10:]:
        text += f"{c['rarity']} — {c['name']}\n"

    await message.answer(text)


# =========================
# 👤 ПРОФИЛЬ (ПОЛНЫЙ)
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["профиль", "📁 профиль"])
async def profile(message: Message):
    user = get_user(message.from_user.id)
    cards = user["cards"]

    rarity_count = {
        "⚪": 0,
        "🟢": 0,
        "🔵": 0,
        "🟣": 0,
        "🟡": 0
    }

    for c in cards:
        rarity_count[c["rarity"]] += 1

    text = f"""
👤 Профиль

🆔 ID: {message.from_user.id}

💎 Премиум • Нет

Активная:
🔵 {user["active"] if user["active"] else "Нет"}

Баланс • {user["balance"]} 🪙
Карточки • {len(cards)} 🎴
Фрагменты • {user["fragments"]} 🧩

🌳 Дерево • {user["tree"]} см

Топ:
🪙 Баланс • #-
🎴 Карточки • #-
🌳 Дерево • #-

Коллекция:
🎴 {len(cards)}  ⚪ {rarity_count["⚪"]}  🟢 {rarity_count["🟢"]}  🔵 {rarity_count["🔵"]}  🟣 {rarity_count["🟣"]}  🟡 {rarity_count["🟡"]}
"""

    await message.answer(text)


# =========================
# ❓ ПОМОЩЬ
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["помощь", "❓ помощь"])
async def help_cmd(message: Message):
    await message.answer(
        "📖 Команды:\n\n"
        "📁 профиль\n"
        "🎴 карта\n"
        "📦 карты"
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
