import asyncio
import random
import time
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ---------------- CONFIG ----------------

TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [8200958216]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- DATA ----------------

users = {}

cards = {
    1: {"name": "Саконжи Урокодаки", "rarity": "common", "file_id": None},
    2: {"name": "Канао Цуюри", "rarity": "uncommon", "file_id": None},
    3: {"name": "Синобу Кочо", "rarity": "rare", "file_id": None},
    4: {"name": "Незуко Камадо", "rarity": "epic", "file_id": None},
    5: {"name": "Гию Тамиока", "rarity": "epic", "file_id": None},
    6: {"name": "Тандзиро Камадо", "rarity": "legendary", "file_id": None},
    7: {"name": "Кокушибо", "rarity": "mythic", "file_id": None},
}

RARITY_EMOJI = {
    "common": "⚪",
    "uncommon": "🟢",
    "rare": "🔵",
    "epic": "🟣",
    "legendary": "🟡",
    "mythic": "🔴",
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

# ---------------- STATE ----------------

view_index = {}
selected_admin_card = {}

class AdminState(StatesGroup):
    waiting_photo = State()

# ---------------- MENU ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 профиль"), KeyboardButton(text="🎒 инвентарь")],
        [KeyboardButton(text="🎴 карта"), KeyboardButton(text="🎁 бонус")],
        [KeyboardButton(text="👁 просмотр"), KeyboardButton(text="🏆 топ")],
        [KeyboardButton(text="🛠 админ")],
    ],
    resize_keyboard=True
)

# ---------------- USER ----------------

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "coins": 100,
            "cards": [],
            "fragments": 0,
            "active_card": None,
            "cooldowns": {"card": 0, "bonus": 0}
        }
    return users[uid]

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(msg: Message):
    get_user(msg.from_user.id)
    await msg.answer("👤 профиль создан", reply_markup=menu)

# ---------------- PROFILE ----------------

@dp.message(F.text == "👤 профиль")
async def profile(msg: Message):
    u = get_user(msg.from_user.id)
    active = cards.get(u.get("active_card"))

    base = (
        f"👤 Профиль\n"
        f"🆔 ID: {msg.from_user.id}\n"
        f"🪙 Баланс • {u['coins']}\n"
        f"🧩 Фрагменты • {u['fragments']}\n"
        f"🎴 Карточек • {len(u['cards'])}"
    )

    if active:
        emoji = RARITY_EMOJI.get(active["rarity"], "⚪")
        text = f"🔥 АКТИВНАЯ КАРТОЧКА\n<blockquote>{emoji} {active['name']}</blockquote>\n\n{base}"
    else:
        text = f"🔥 АКТИВНАЯ КАРТОЧКА\n<blockquote>нет</blockquote>\n\n{base}"

    if active and active["file_id"]:
        await msg.answer_photo(active["file_id"], caption=text, parse_mode="HTML")
    else:
        await msg.answer(text, parse_mode="HTML")

# ---------------- BONUS ----------------

@dp.message(F.text == "🎁 бонус")
async def bonus(msg: Message):
    u = get_user(msg.from_user.id)

    if time.time() < u["cooldowns"]["bonus"]:
        return await msg.answer("⏳ бонус недоступен")

    reward = random.randint(50, 100)
    u["coins"] += reward
    u["cooldowns"]["bonus"] = time.time() + 86400

    await msg.answer(f"🎁 +{reward} 🪙")

# ---------------- CARD ----------------

def roll_rarity():
    r = random.uniform(0, 100)
    s = 0
    for name, chance in RARITY_CHANCE:
        s += chance
        if r <= s:
            return name
    return "common"

@dp.message(F.text == "🎴 карта")
async def card(msg: Message):
    u = get_user(msg.from_user.id)

    if time.time() < u["cooldowns"]["card"]:
        return await msg.answer("⏳ подожди 4 часа")

    rarity = roll_rarity()
    card_id = random.choice(list(cards.keys()))
    card = cards[card_id]

    coins = random.randint(*RARITY_COINS[rarity])

    u["cards"].append(card_id)
    u["fragments"] += 1
    u["coins"] += coins
    u["cooldowns"]["card"] = time.time() + 14400

    if not u["active_card"]:
        u["active_card"] = card_id

    emoji = RARITY_EMOJI.get(rarity, "⚪")

    text = f"🎴 НОВАЯ КАРТА\n\n{emoji} {card['name']}\n\n💰 +{coins} 🪙"

    if card["file_id"]:
        await msg.answer_photo(card["file_id"], caption=text)
    else:
        await msg.answer(text)

# ---------------- VIEW ----------------

@dp.message(F.text == "👁 просмотр")
async def view_start(msg: Message):
    view_index[msg.from_user.id] = 0
    await show_view(msg)

async def show_view(event):
    uid = event.from_user.id
    index = view_index.get(uid, 0)

    all_cards = list(cards.items())

    if not all_cards:
        return await event.answer("нет карточек")

    if index < 0:
        index = 0
    if index >= len(all_cards):
        index = len(all_cards) - 1

    view_index[uid] = index

    cid, c = all_cards[index]

    emoji = RARITY_EMOJI.get(c["rarity"], "⚪")

    text = f"""
🎴 КАРТОЧКА

{emoji} {c['name']}

📝 редкость: {c['rarity']}
"""

    nav = []

    if index > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data="view_prev"))
    if index < len(all_cards) - 1:
        nav.append(InlineKeyboardButton(text="➡️", callback_data="view_next"))

    kb = InlineKeyboardMarkup(inline_keyboard=[nav])

    if c["file_id"]:
        await event.answer_photo(c["file_id"], caption=text, reply_markup=kb)
    else:
        await event.answer(text, reply_markup=kb)

@dp.callback_query(F.data == "view_next")
async def next_card(c: CallbackQuery):
    view_index[c.from_user.id] = view_index.get(c.from_user.id, 0) + 1
    await show_view(c.message)

@dp.callback_query(F.data == "view_prev")
async def prev_card(c: CallbackQuery):
    view_index[c.from_user.id] = max(0, view_index.get(c.from_user.id, 0) - 1)
    await show_view(c.message)

# ---------------- TOP ----------------

@dp.message(F.text == "🏆 топ")
async def top(msg: Message):
    top_list = sorted(users.items(), key=lambda x: x[1]["coins"], reverse=True)[:10]

    text = "🏆 ТОП\n\n"
    for i, (uid, u) in enumerate(top_list, 1):
        text += f"{i}. {uid} - {u['coins']} 🪙\n"

    await msg.answer(text)

# ---------------- ADMIN ----------------

@dp.message(F.text == "🛠 админ")
async def admin(msg: Message):
    if msg.from_user.id not in ADMINS:
        return

    text = "🛠 КАРТОЧКИ\n\n"
    kb = []

    for cid, c in cards.items():
        emoji = RARITY_EMOJI.get(c["rarity"], "⚪")
        text += f"{cid}. {emoji} {c['name']}\n"
        kb.append([InlineKeyboardButton(text=c["name"], callback_data=f"adm_{cid}")])

    await msg.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data.startswith("adm_"))
async def adm(c: CallbackQuery, state: FSMContext):
    cid = int(c.data.split("_")[1])
    selected_admin_card[c.from_user.id] = cid
    await state.set_state(AdminState.waiting_photo)
    await c.message.answer("отправь фото")

@dp.message(AdminState.waiting_photo, F.photo)
async def save_photo(m: Message, state: FSMContext):
    cid = selected_admin_card.get(m.from_user.id)
    cards[cid]["file_id"] = m.photo[-1].file_id
    await m.answer("сохранено")
    await state.clear()

# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
