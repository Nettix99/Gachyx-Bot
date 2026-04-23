import asyncio
import random
import time
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [8200958216]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------ DATA ------------------

users = {}

cards = {
    1: {"name": "Саконжи Урокодаки", "rarity": "common", "file_id": None},
    2: {"name": "Канао Цуюри", "rarity": "uncommon", "file_id": None},
    3: {"name": "Синобу Кочо", "rarity": "rare", "file_id": None},
}

# ------------------ STATES ------------------

class AdminState(StatesGroup):
    choosing_card = State()
    waiting_photo = State()

selected_card = {}

# ------------------ UI ------------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 профиль")],
        [KeyboardButton(text="🎒 инвентарь")],
        [KeyboardButton(text="🎴 карта")],
        [KeyboardButton(text="🎁 бонус")],
        [KeyboardButton(text="🛠 админ")],
    ],
    resize_keyboard=True
)

# ------------------ USER ------------------

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "coins": 100,
            "cards": [],
            "fragments": 0,
            "cooldowns": {"card": 0, "bonus": 0}
        }
    return users[uid]

# ------------------ START ------------------

@dp.message(F.text == "/start")
async def start(msg: Message):
    get_user(msg.from_user.id)
    await msg.answer("👤 профиль создан", reply_markup=menu)

# ------------------ PROFILE ------------------

@dp.message(F.text == "👤 профиль")
async def profile(msg: Message):
    u = get_user(msg.from_user.id)
    await msg.answer(f"👤 Профиль\n🪙 {u['coins']}\n🎴 {len(u['cards'])}\n🧩 {u['fragments']}")

# ------------------ ADMIN PANEL ------------------

@dp.message(F.text == "🛠 админ")
async def admin(msg: Message, state: FSMContext):
    if msg.from_user.id not in ADMINS:
        return await msg.answer("нет доступа")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c["name"], callback_data=f"card_{cid}")]
        for cid, c in cards.items()
    ])

    await msg.answer("выбери карточку", reply_markup=kb)
    await state.set_state(AdminState.choosing_card)

# ------------------ SELECT CARD ------------------

@dp.callback_query(F.data.startswith("card_"))
async def select_card(call: CallbackQuery, state: FSMContext):
    cid = int(call.data.split("_")[1])

    selected_card[call.from_user.id] = cid

    await state.set_state(AdminState.waiting_photo)
    await call.message.answer(f"отправь фото для: {cards[cid]['name']}")
    await call.answer()

# ------------------ PHOTO SAVE ------------------

@dp.message(AdminState.waiting_photo, F.photo)
async def save_photo(msg: Message, state: FSMContext):
    if msg.from_user.id not in ADMINS:
        return

    cid = selected_card.get(msg.from_user.id)
    if not cid:
        return

    file_id = msg.photo[-1].file_id
    cards[cid]["file_id"] = file_id

    await msg.answer(f"готово: {cards[cid]['name']}")

    await state.clear()

# ------------------ CARD ROLL ------------------

@dp.message(F.text == "🎴 карта")
async def card(msg: Message):
    u = get_user(msg.from_user.id)

    if time.time() < u["cooldowns"]["card"]:
        return await msg.answer("⏳ подожди")

    card = random.choice(list(cards.values()))

    u["cards"].append(card["name"])
    u["fragments"] += 1
    u["coins"] += random.randint(10, 80)

    u["cooldowns"]["card"] = time.time() + 14400

    if card["file_id"]:
        await msg.answer_photo(card["file_id"], caption=card["name"])
    else:
        await msg.answer(card["name"])

# ------------------ BONUS ------------------

@dp.message(F.text == "🎁 бонус")
async def bonus(msg: Message):
    u = get_user(msg.from_user.id)

    if time.time() < u["cooldowns"]["bonus"]:
        return await msg.answer("⏳ нельзя")

    reward = random.randint(50, 100)
    u["coins"] += reward
    u["cooldowns"]["bonus"] = time.time() + 86400

    await msg.answer(f"+{reward} 🪙")

# ------------------ RUN ------------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
