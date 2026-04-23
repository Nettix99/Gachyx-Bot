import asyncio
import random
import time
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8783833879:AAGu7m564GaYTjcA6NGV4IS7UpHMVUieoO8"
ADMINS = [8200958216]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------ ДАННЫЕ ------------------

users = {}
cards = {
    1: {"name": "Саконжи Урокодаки", "rarity": "common", "file_id": None},
    2: {"name": "Канао Цуюри", "rarity": "uncommon", "file_id": None},
    3: {"name": "Синобу Кочо", "rarity": "rare", "file_id": None},
}

RARITY_CHANCE = [
    ("common", 58),
    ("uncommon", 25),
    ("rare", 12),
    ("epic", 4),
    ("legendary", 0.9),
    ("mythic", 0.1),
]

RARITY_COINS = {
    "common": (10, 20),
    "uncommon": (20, 40),
    "rare": (40, 80),
    "epic": (80, 150),
    "legendary": (150, 300),
    "mythic": (300, 600),
}

# ------------------ UI ------------------

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 профиль")],
        [KeyboardButton(text="🎒 инвентарь")],
        [KeyboardButton(text="🎴 карта")],
        [KeyboardButton(text="🎁 бонус")],
    ],
    resize_keyboard=True
)

# ------------------ UTIL ------------------

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "coins": 100,
            "cards": [],
            "fragments": 0,
            "active": None,
            "cooldowns": {"card": 0, "bonus": 0}
        }
    return users[uid]

def roll_rarity():
    r = random.uniform(0, 100)
    s = 0
    for name, chance in RARITY_CHANCE:
        s += chance
        if r <= s:
            return name
    return "common"

def get_card_by_rarity(rarity):
    pool = [c for c in cards.values() if c["rarity"] == rarity]
    return random.choice(pool) if pool else None

# ------------------ START ------------------

@dp.message(F.text == "/start")
async def start(msg: Message):
    get_user(msg.from_user.id)
    await msg.answer("👤 профиль создан", reply_markup=menu_kb)

# ------------------ PROFILE ------------------

@dp.message(F.text == "👤 профиль")
async def profile(msg: Message):
    u = get_user(msg.from_user.id)
    await msg.answer(
        f"""👤 Профиль

🪙 {u['coins']}
🎴 {len(u['cards'])}
🧩 {u['fragments']}
"""
    )

# ------------------ BONUS ------------------

@dp.message(F.text == "🎁 бонус")
async def bonus(msg: Message):
    u = get_user(msg.from_user.id)
    now = time.time()

    if now < u["cooldowns"]["bonus"]:
        return await msg.answer("⏳ бонус недоступен")

    reward = random.randint(50, 100)
    u["coins"] += reward
    u["cooldowns"]["bonus"] = now + 86400

    await msg.answer(f"🎁 +{reward} 🪙")

# ------------------ CARD ------------------

@dp.message(F.text == "🎴 карта")
async def card(msg: Message):
    u = get_user(msg.from_user.id)
    now = time.time()

    if now < u["cooldowns"]["card"]:
        return await msg.answer("⏳ подожди 4 часа")

    rarity = roll_rarity()
    card = get_card_by_rarity(rarity)

    if not card:
        return await msg.answer("нет карточек")

    coins = random.randint(*RARITY_COINS[rarity])

    u["cards"].append(card["name"])
    u["fragments"] += 1
    u["coins"] += coins
    u["cooldowns"]["card"] = now + 14400

    text = f"""🎴 карта

{card['name']}
редкость: {rarity}

+1 🧩
+{coins} 🪙"""

    await msg.answer(text)

# ------------------ INVENTORY ------------------

@dp.message(F.text == "🎒 инвентарь")
async def inv(msg: Message):
    u = get_user(msg.from_user.id)

    if not u["cards"]:
        return await msg.answer("пусто")

    text = "🎒 инвентарь\n\n"
    for i, c in enumerate(u["cards"], 1):
        text += f"{i}. {c}\n"

    await msg.answer(text)

# ------------------ ADMIN SET PHOTO ------------------

@dp.message(F.photo)
async def admin_photo(msg: Message):
    if msg.from_user.id not in ADMINS:
        return

    if not hasattr(msg, "reply_to_message") or not msg.reply_to_message:
        return

    try:
        card_id = int(msg.reply_to_message.text.split(":")[1])
    except:
        return

    file_id = msg.photo[-1].file_id
    cards[card_id]["file_id"] = file_id

    await msg.answer(f"готово: {cards[card_id]['name']}")

# ------------------ RUN ------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
