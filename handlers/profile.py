from aiogram import Router
from aiogram.types import Message
from db import get_user

router = Router()

@router.message(lambda m: m.text and m.text.lower().strip() in ["профиль", "/profile", "📁 профиль"])
async def profile(message: Message):
    user = await get_user(message.from_user.id)

    await message.answer(f"""
👤 Профиль

🆔 ID: {message.from_user.id}
💎 Премиум • {"Да" if user['premium'] else "Нет"}

🪙 Баланс • {user['balance']}
🎴 Карточки • {user['cards']}
🧩 Фрагменты • {user['fragments']}

🌳 Дерево • {user['tree']} см
""")
