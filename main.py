from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN
from loader.modules_loader import register_all
from database.models import create_tables

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# создаём таблицы
create_tables()

# регистрируем модули
register_all(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
