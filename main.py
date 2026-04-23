import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from db import connect, create_tables

from handlers import profile, card, help  # оставь только реально существующие

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# подключаем хендлеры
dp.include_router(profile.router)
dp.include_router(card.router)
dp.include_router(help.router)


async def main():
    print("🚀 BOT STARTING...")

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN is empty")
        return

    await connect()
    print("✅ DB CONNECTED")

    await create_tables()
    print("✅ TABLES READY")

    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ WEBHOOK CLEARED")

    print("🔥 START POLLING")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
