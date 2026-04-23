import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN
from db import connect, create_tables, create_user

# handlers
from handlers import profile, card, help

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 📌 Авто-регистрация пользователя
@dp.message()
async def ensure_user(message: Message):
    await create_user(message.from_user.id)

# 🔗 Роутеры
dp.include_router(profile.router)
dp.include_router(card.router)
dp.include_router(help.router)

async def main():
    await connect()
    await create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
