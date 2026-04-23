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

RARITY_EMOJI = {
    "common": "⚪",
    "uncommon": "🟢",
    "rare": "🔵",
    "epic": "🟣",
    "legendary": "🟡",
    "mythic": "🔴",
}

# ---------------- STATE ----------------

user_inv_page = {}
user_inv_rarity = {}
selected_card_inv = {}
selected_admin_card = {}

class AdminState(StatesGroup):
    choosing_card = State()
    waiting_photo = State()

# ---------------- MENU ----------------

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 профиль")],
        [KeyboardButton(text="🎒 инвентарь")],
        [KeyboardButton(text="🎴 карта")],
        [KeyboardButton(text="🎁 бонус")],
        [KeyboardButton(text="🏆 топ")],
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

# ---------------- PROFILE (FIXED UI) ----------------

@dp.message(F.text == "👤 профиль")
async def profile(msg: Message):
    u = get_user(msg.from_user.id)
    active = cards.get(u.get("active_card"))

    base = (
        f"👤 Профиль\n"
        f"🆔 ID: {msg.from_user.id}\n"
        f"💎 Премиум • {'Да' if u['premium'] else 'Нет'}\n"
        f"🪙 Баланс • {u['coins']}\n"
        f"🧩 Фрагменты • {u['fragments']}\n"
        f"🎴 Карточек • {len(u['cards'])}"
    )

    if active:
        emoji = RARITY_EMOJI.get(active["rarity"], "⚪")

        text = (
            "🔥 АКТИВНАЯ КАРТОЧКА\n"
            f"<blockquote>{emoji} {active['name']}</blockquote>\n\n"
            f"{base}"
        )
    else:
        text = (
            "🔥 АКТИВНАЯ КАРТОЧКА\n"
            "<blockquote>нет</blockquote>\n\n"
            f"{base}"
        )

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

# ---------------- CARD SYSTEM ----------------

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

    text = (
        "🎴 НОВАЯ КАРТА\n\n"
        f"{emoji} {card['name']}\n\n"
        f"💰 +{coins} 🪙\n"
        f"🧩 +1"
    )

    if card["file_id"]:
        await msg.answer_photo(card["file_id"], caption=text)
    else:
        await msg.answer(text)

# ---------------- INVENTORY ----------------

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

@dp.callback_query(F.data.startswith("r_"))
async def rarity(call: CallbackQuery):
    r = call.data.split("_")[1]
    user_inv_rarity[call.from_user.id] = r
    user_inv_page[call.from_user.id] = 0
    await show_inventory(call)

def get_cards_by_rarity(uid, rarity):
    u = get_user(uid)
    res = []
    for cid in u["cards"]:
        c = cards.get(cid)
        if c and c["rarity"] == rarity:
            res.append({"id": cid, **c})
    return res

async def show_inventory(call: CallbackQuery):
    uid = call.from_user.id
    u = get_user(uid)

    rarity = user_inv_rarity.get(uid, "common")
    page = user_inv_page.get(uid, 0)

    items = get_cards_by_rarity(uid, rarity)

    start = page * 5
    end = start + 5
    page_items = items[start:end]

    active = cards.get(u.get("active_card"))

    text = f"🎒 {rarity.upper()}\n\n"

    if active:
        emoji = RARITY_EMOJI.get(active["rarity"], "⚪")
        text += f"🔥 АКТИВНАЯ\n<blockquote>{emoji} {active['name']}</blockquote>\n\n"

    kb = []

    for i, c in enumerate(page_items, 1):
        emoji = RARITY_EMOJI.get(c["rarity"], "⚪")
        text += f"{i}️⃣ {emoji} {c['name']}\n"
        kb.append([InlineKeyboardButton(text=f"{i}️⃣", callback_data=f"card_{c['id']}")])

    nav = []

    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️", callback_data="inv_prev"))
    if end < len(items):
        nav.append(InlineKeyboardButton(text="➡️", callback_data="inv_next"))

    nav.append(InlineKeyboardButton(text="🔙", callback_data="inv_back"))

    kb.append(nav)

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

@dp.callback_query(F.data == "inv_next")
async def nxt(c: CallbackQuery):
    user_inv_page[c.from_user.id] = user_inv_page.get(c.from_user.id, 0) + 1
    await show_inventory(c)

@dp.callback_query(F.data == "inv_prev")
async def prv(c: CallbackQuery):
    user_inv_page[c.from_user.id] = max(0, user_inv_page.get(c.from_user.id, 0) - 1)
    await show_inventory(c)

@dp.callback_query(F.data == "inv_back")
async def back(c: CallbackQuery):
    await inventory(c.message)

# ---------------- SELECT CARD ----------------

@dp.callback_query(F.data.startswith("card_"))
async def select(c: CallbackQuery):
    cid = int(c.data.split("_")[1])
    selected_card_inv[c.from_user.id] = cid

    card = cards[cid]
    emoji = RARITY_EMOJI.get(card["rarity"], "⚪")

    text = f"🎴 КАРТА\n\n{emoji} {card['name']}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ активировать", callback_data="set_active")]
    ])

    if card["file_id"]:
        await c.message.answer_photo(card["file_id"], caption=text, reply_markup=kb)
    else:
        await c.message.answer(text, reply_markup=kb)

@dp.callback_query(F.data == "set_active")
async def set_active(c: CallbackQuery):
    uid = c.from_user.id
    cid = selected_card_inv.get(uid)

    if cid:
        get_user(uid)["active_card"] = cid
        await c.answer("установлено")

# ---------------- TOP ----------------

@dp.message(F.text == "🏆 топ")
async def top(msg: Message):
    top_list = sorted(users.items(), key=lambda x: x[1]["coins"], reverse=True)[:10]

    text = "🏆 ТОП\n\n🪙 Баланс:\n"

    for i, (uid, u) in enumerate(top_list, 1):
        text += f"{i}. {uid} - {u['coins']} 🪙\n"

    await msg.answer(text)

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
