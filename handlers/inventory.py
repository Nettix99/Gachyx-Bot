from aiogram import Router
from aiogram.types import Message
from db import get_user

router = Router()

@router.message(lambda m: m.text and m.text.lower().strip() in ["карты", "/cards", "📦 карты"])
async def inventory(message: Message):
    user = await get_user(message.from_user.id)

    await message.answer(f"""
📦 Инвентарь

🎴 Карты: {user['cards']}
🧩 Фрагменты: {user['fragments']}
""")
