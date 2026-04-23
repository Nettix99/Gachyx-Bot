import asyncio import logging

from aiogram import Bot, Dispatcher, F from aiogram.filters import CommandStart from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN) dp = Dispatcher()

=========================

⚙️ CONFIG

=========================

ADMIN_ID = 8200958216 LOG_CHAT_ID = -1003774664852

=========================

🧠 MEMORY

=========================

USERS = {}

3 тестовые карточки

CARDS = { 1: { "name": "Тандзиро Камадо", "rarity": "🟡", "photo_id": None }, 2: { "name": "Наруто Узумаки", "rarity": "🔵", "photo_id": None }, 3: { "name": "Леви Аккерман", "rarity": "🟣", "photo_id": None } }

=========================

TEMP ADMIN STATE

=========================

admin_state = { "edit_card_id": None }

=========================

USER

=========================

def get_user(user_id: int): if user_id not in USERS: USERS[user_id] = { "cards": [1, 2], "active_card": 1, "balance": 0, "fragments": 0, "tree": 120, "premium": True } return USERS[user_id]

=========================

START

=========================

@dp.message(CommandStart()) async def start(message: Message): get_user(message.from_user.id)

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📁 Профиль"), KeyboardButton(text="🎴 Карта")],
        [KeyboardButton(text="📦 Инвентарь"), KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True
)

await message.answer("👋 CardBot запущен", reply_markup=kb)

=========================

📁 ПРОФИЛЬ

=========================

@dp.message(lambda m: m.text and m.text.lower() in ["профиль", "📁 профиль"]) async def profile(message: Message): user = get_user(message.from_user.id) active = CARDS[user["active_card"]]

text = f"""

👤 Профиль

🆔 ID • {message.from_user.id}

🎴 Активная карточка: {active['name']} ⭐ Редкость • {active['rarity']} 🆔 ID карты • {user['active_card']}

💰 Баланс • {user['balance']} 🪙 📦 Карточки • {len(user['cards'])} 🎴 """

if active["photo_id"]:
    await message.answer_photo(
        photo=active["photo_id"],
        caption=text
    )
else:
    await message.answer(text)

=========================

📦 ИНВЕНТАРЬ

=========================

@dp.message(lambda m: m.text and m.text.lower() in ["инвентарь", "📦 инвентарь"]) async def inventory(message: Message): user = get_user(message.from_user.id)

text = "📦 Инвентарь:\n\n"

for cid in user["cards"]:
    card = CARDS[cid]
    active_mark = " ✅ АКТИВНА" if cid == user["active_card"] else ""

    text += (
        f"🎴 ID: {cid}\n"
        f"🏷 {card['name']}\n"
        f"⭐ {card['rarity']}{active_mark}\n"
        f"➡ Напиши: выбрать {cid}\n\n"
    )

await message.answer(text)

=========================

🎯 УСТАНОВКА АКТИВНОЙ КАРТЫ

=========================

@dp.message(lambda m: m.text and m.text.lower().startswith("выбрать")) async def set_active(message: Message): user = get_user(message.from_user.id)

try:
    cid = int(message.text.split()[1])
except:
    return await message.answer("❌ Используй: выбрать <id>")

if cid not in user["cards"]:
    return await message.answer("❌ У тебя нет такой карты")

user["active_card"] = cid

await message.answer(
    f"✅ Активная карточка установлена:\n\n"
    f"{CARDS[cid]['name']}\n"
    f"⭐ {CARDS[cid]['rarity']}"
)

=========================

🎴 ВЫДАТЬ ТЕСТОВУЮ КАРТУ

=========================

@dp.message(lambda m: m.text and m.text.lower() in ["карта", "🎴 карта"]) async def give_card(message: Message): user = get_user(message.from_user.id)

user["cards"].append(3)

await message.answer(
    "🎴 Получена новая карта!\n\n"
    "Леви Аккерман\n"
    "⭐ 🟣"
)

=========================

🛠 АДМИН ПАНЕЛЬ

=========================

@dp.message(lambda m: m.text and m.text.lower() == "админ") async def admin_panel(message: Message): if message.from_user.id != ADMIN_ID: return await message.answer("⛔ Нет доступа")

cards_text = "\n".join(
    [f"{cid} — {card['name']} {card['rarity']}" for cid, card in CARDS.items()]
)

await message.answer(
    "🛠 Админ панель\n\n"
    "Список карт:\n\n"
    f"{cards_text}\n\n"
    "Для изменения фото напиши:\n"
    "редактировать <id>"
)

=========================

🎯 ВЫБОР КАРТЫ ДЛЯ РЕДАКТИРОВАНИЯ

=========================

@dp.message(lambda m: m.text and m.text.lower().startswith("редактировать")) async def edit_card(message: Message): if message.from_user.id != ADMIN_ID: return

try:
    cid = int(message.text.split()[1])
except:
    return await message.answer("❌ Используй: редактировать <id>")

if cid not in CARDS:
    return await message.answer("❌ Такой карты не существует")

admin_state["edit_card_id"] = cid

await message.answer(
    f"📸 Отправь новое фото для карты:\n\n"
    f"{CARDS[cid]['name']}\n"
    f"⭐ {CARDS[cid]['rarity']}"
)

=========================

📸 УСТАНОВКА ФОТО КАРТЫ

=========================

@dp.message(F.photo) async def handle_photo(message: Message): if message.from_user.id != ADMIN_ID: return

cid = admin_state.get("edit_card_id")

if not cid:
    return await message.answer(
        "❌ Сначала выбери карту:\nредактировать <id>"
    )

file_id = message.photo[-1].file_id
CARDS[cid]["photo_id"] = file_id

await bot.send_photo(
    chat_id=LOG_CHAT_ID,
    photo=file_id,
    caption=(
        "🖼 Фото карточки обновлено\n\n"
        f"ID: {cid}\n"
        f"🏷 {CARDS[cid]['name']}\n"
        f"⭐ {CARDS[cid]['rarity']}"
    )
)

await message.answer("✅ Фото карточки успешно обновлено")

admin_state["edit_card_id"] = None

=========================

❓ ПОМОЩЬ

=========================

@dp.message(lambda m: m.text and m.text.lower() in ["помощь", "❓ помощь"]) async def help_command(message: Message): await message.answer( "❓ Команды:\n\n" "📁 Профиль — посмотреть профиль\n" "📦 Инвентарь — список карт\n" "🎴 Карта — получить тестовую карту\n" "выбрать <id> — сделать карту активной\n\n" "🛠 Для админа:\n" "админ\n" "редактировать <id>" )

=========================

🚀 START

=========================

async def main(): await bot.delete_webhook(drop_pending_updates=True) await dp.start_polling(bot)

if name == "main": asyncio.run(main())
