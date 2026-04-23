import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN
from db import connect, create_tables

# handlers
from handlers import (
    profile,
    card,
    inventory,
    market,
    bonus,
    tree,
    water,
    help_handler
)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# 📌 HANDLERS
# =========================
dp.include_router(profile.router)
dp.include_router(card.router)
dp.include_router(inventory.router)
dp.include_router(market.router)
dp.include_router(bonus.router)
dp.include_router(tree.router)
dp.include_router(water.router)
dp.include_router(help_handler.router)

# =========================
# 💬 START (ЛС)
# =========================
@dp.message(CommandStart())
async def start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📁 Профиль"), KeyboardButton(text="🎴 Карта")],
            [KeyboardButton(text="📦 Карты"), KeyboardButton(text="🌳 Дерево")],
            [KeyboardButton(text="🔄 Рынок"), KeyboardButton(text="🎁 Бонус")],
            [KeyboardButton(text="💧 Полить"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

    await message.answer("👋 Добро пожаловать в CardBot!", reply_markup=kb)

# =========================
# 🚀 MAIN
# =========================
async def main():
    print("🚀 BOT STARTING...")

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN is empty")
        return

    await connect()
    await create_tables()

    await bot.delete_webhook(drop_pending_updates=True)

    print("🔥 BOT IS RUNNING")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
