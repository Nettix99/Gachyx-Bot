import asyncio
import logging
import time

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
ADMIN_ID = 8200958216
LOG_CHAT_ID = -1003774664852

CARD_COOLDOWN = 4 * 60 * 60  # 4 часа

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
            "cards": [],
            "balance": 0,
            "fragments": 0,
            "tree": 120,
            "premium": True,
            "last_card_time": 0
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
# 🎴 КАРТА (С КД 4 ЧАСА)
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["карта", "🎴 карта"])
async def give_card(message: Message):
    user = get_user(message.from_user.id)

    now = time.time()
    last = user.get("last_card_time", 0)

    if now - last < CARD_COOLDOWN:
        remaining = int(CARD_COOLDOWN - (now - last))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60

        return await message.answer(
            f"⏳ Подожди КД!\n"
            f"Осталось: {hours}ч {minutes}м"
        )

    user["last_card_time"] = now
    user["cards"].append(CARD["id"])

    text = (
        f"🎴 Карта получена!\n\n"
        f"🏷 {CARD['name']}\n"
        f"⭐ {CARD['rarity']}"
    )

    if CARD["photo_id"]:
        await message.answer_photo(CARD["photo_id"], caption=text)
    else:
        await message.answer(text)


# =========================
# 📦 КАРТЫ
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

    balance = user["balance"]
    fragments = user["fragments"]
    tree = user["tree"]
    cards = user["cards"]

    rarity = {
        "⚪": 0,
        "🟢": 0,
        "🔵": 0,
        "🟣": 0,
        "🟡": len(cards)
    }

    text = f"""
👤 Профиль

🆔 ID • {message.from_user.id}

💎 Премиум • {"Да" if user["premium"] else "Нет"}

Активная:
🔵 {CARD["name"]}

Баланс • {balance} 🪙
Карточки • {len(cards)} 🎴
Фрагменты • {fragments} 🧩

🌳 Дерево • {tree} см

Топ:
🪙 Баланс • #1
🎴 Карточки • #1
🌳 Дерево • #1

Коллекция:
🎴 {len(cards)}  ⚪ {rarity["⚪"]}  🟢 {rarity["🟢"]}  🔵 {rarity["🔵"]}  🟣 {rarity["🟣"]}  🟡 {rarity["🟡"]}
"""

    await message.answer(text)


# =========================
# 🛠 АДМИН
# =========================
@dp.message(lambda m: m.text and m.text.lower() == "админ")
async def admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа")

    await message.answer("🛠 Админ режим\n📸 отправь фото для карты")


# =========================
# 📸 ФОТО (АДМИН)
# =========================
@dp.message(F.photo)
async def handle_photo(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    file_id = message.photo[-1].file_id
    CARD["photo_id"] = file_id

    await bot.send_photo(
        LOG_CHAT_ID,
        photo=file_id,
        caption=f"🖼 Новая карта\n🎴 {CARD['name']}\n⭐ {CARD['rarity']}\nID: {file_id}"
    )

    await message.answer("✅ Сохранено")


# =========================
# ❓ HELP
# =========================
@dp.message(lambda m: m.text and m.text.lower() in ["помощь", "❓ помощь"])
async def help_cmd(message: Message):
    await message.answer(
        "📖 Команды:\n"
        "📁 профиль\n"
        "🎴 карта\n"
        "📦 карты\n"
        "админ"
    )


# =========================
# 🚀 START
# =========================
async def main():
    print("🚀 BOT STARTED")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
