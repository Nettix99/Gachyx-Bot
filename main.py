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

# ---------------- INVENTORY STATE ----------------

user_inv_page = {}
user_inv_rarity = {}
selected_card_inv = {}

# ---------------- ADMIN STATE ----------------

class AdminState(StatesGroup):
    choosing_card = State()
    waiting_photo = State()

selected_admin_card = {}

# ---------------- UI ----------------

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

# ---------------- USER ----------------

def get_user(uid):
    if uid not in users:
        users[uid] = {
            "coins": 100,
            "cards": [],
            "fragments": 0,
            "premium": False,
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

    active = u.get("active_card") or "нет"

    text = f"""
👤 Профиль

🆔 ID: {msg.from_user.id}

💎 Премиум • {'Да' if u['premium'] else 'Нет'}

Активная:
{active}

────────────────
🪙 Баланс • {u['coins']}
🧩 Фрагменты • {u['fragments']}

────────────────
🎴 Карточки • {len(u['cards'])}
"""

    await msg.answer(text)

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

def get_card_by_rarity(rarity):
    pool = [c for c in cards.values() if c["rarity"] == rarity]
    return random.choice(pool) if pool else None

@dp.message(F.text == "🎴 карта")
async def card(msg: Message):
    u = get_user(msg.from_user.id)

    if time.time() < u["cooldowns"]["card"]:
        return await msg.answer("⏳ подожди 4 часа")

    rarity = roll_rarity()
    card = get_card_by_rarity(rarity)

    if not card:
        return await msg.answer("нет карточек")

    coins = random.randint(*RARITY_COINS[rarity])

    u["cards"].append(card["name"])
    u["fragments"] += 1
    u["coins"] += coins
    u["cooldowns"]["card"] = time.time() + 14400

    if card["file_id"]:
        await msg.answer_photo(card["file_id"], caption=card["name"])
    else:
        await msg.answer(card["name"])

# ---------------- INVENTORY RPG ----------------

def get_cards_by_rarity(uid, rarity):
    u = get_user(uid)
    result = []
    for c in u["cards"]:
        card = next((x for x in cards.values() if x["name"] == c), None)
        if card and card["rarity"] == rarity:
            result.append(card)
    return result

@dp.message(F.text == "🎒 инвентарь")
async def inventory(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚪", callback_data="r_common"),
            InlineKeyboardButton(text="🟢", callback_data="r_uncommon"),
            InlineKeyboardButton(text="🔵", callback_data="r_rare"),
        ],
        [
            InlineKeyboardButton(text="🟣", callback_data="r_epic"),
            InlineKeyboardButton(text="🟡", callback_data="r_legendary"),
            InlineKeyboardButton(text="🔴", callback_data="r_mythic"),
        ],
    ])

    await msg.answer("🎒 выбери редкость", reply_markup=kb)

# ---------------- RARITY ----------------

@dp.callback_query(F.data.startswith("r_"))
async def rarity(call: CallbackQuery):
    rarity = call.data.split("_")[1]

    user_inv_rarity[call.from_user.id] = rarity
    user_inv_page[call.from_user.id] = 0

    await show_inventory(call)

# ---------------- SHOW INVENTORY ----------------

async def show_inventory(call: CallbackQuery):
    uid = call.from_user.id
    rarity = user_inv_rarity.get(uid, "common")
    page = user_inv_page.get(uid, 0)

    items = get_cards_by_rarity(uid, rarity)

    start = page * 5
    end = start + 5
    page_items = items[start:end]

    text = f"🎒 {rarity.upper()} (стр {page+1})\n\n"

    kb = []

    for i, c in enumerate(page_items, 1):
        text += f"{i}️⃣ {c['name']}\n"
        kb.append([InlineKeyboardButton(text=f"{i}️⃣", callback_data=f"card_{c['name']}")])

    nav = []

    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data="inv_prev"))
    if end < len(items):
        nav.append(InlineKeyboardButton(text="➡️", callback_data="inv_next"))

    nav.append(InlineKeyboardButton(text="🔙", callback_data="inv_back"))

    kb.append(nav)

    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# ---------------- NAV ----------------

@dp.callback_query(F.data == "inv_next")
async def next(call: CallbackQuery):
    uid = call.from_user.id
    user_inv_page[uid] += 1
    await show_inventory(call)

@dp.callback_query(F.data == "inv_prev")
async def prev(call: CallbackQuery):
    uid = call.from_user.id
    user_inv_page[uid] = max(0, user_inv_page.get(uid, 0) - 1)
    await show_inventory(call)

@dp.callback_query(F.data == "inv_back")
async def back(call: CallbackQuery):
    await inventory(call.message)

# ---------------- CARD SELECT ----------------

@dp.callback_query(F.data.startswith("card_"))
async def select_card(call: CallbackQuery):
    name = call.data.replace("card_", "")
    uid = call.from_user.id

    selected_card_inv[uid] = name

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐", callback_data="set_active")],
    ])

    await call.message.answer(f"🎴 {name}", reply_markup=kb)

# ---------------- SET ACTIVE ----------------

@dp.callback_query(F.data == "set_active")
async def set_active(call: CallbackQuery):
    uid = call.from_user.id
    name = selected_card_inv.get(uid)

    if not name:
        return await call.answer("нет карты")

    u = get_user(uid)
    u["active_card"] = name

    await call.answer("установлено")

# ---------------- ADMIN ----------------

@dp.message(F.text == "🛠 админ")
async def admin(msg: Message, state: FSMContext):
    if msg.from_user.id not in ADMINS:
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=c["name"], callback_data=f"adm_{cid}")]
        for cid, c in cards.items()
    ])

    await msg.answer("выбери карточку", reply_markup=kb)
    await state.set_state(AdminState.choosing_card)

@dp.callback_query(F.data.startswith("adm_"))
async def admin_select(call: CallbackQuery, state: FSMContext):
    cid = int(call.data.split("_")[1])
    selected_admin_card[call.from_user.id] = cid

    await state.set_state(AdminState.waiting_photo)
    await call.message.answer(f"отправь фото: {cards[cid]['name']}")

@dp.message(AdminState.waiting_photo, F.photo)
async def save_photo(msg: Message, state: FSMContext):
    if msg.from_user.id not in ADMINS:
        return

    cid = selected_admin_card.get(msg.from_user.id)
    if not cid:
        return

    file_id = msg.photo[-1].file_id
    cards[cid]["file_id"] = file_id

    await msg.answer(f"готово: {cards[cid]['name']}")
    await state.clear()

# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
