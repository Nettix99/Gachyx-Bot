from aiogram import Router
from aiogram.types import Message
from db import get_user

router = Router()

@router.message(lambda msg: msg.text.lower() in ["профиль", "/profile"])
async def profile_cmd(message: Message):
    user = await get_user(message.from_user.id)

    text = f"""
👤 Профиль

🆔 ID: {message.from_user.id}
💎 Премиум • {"Да" if user['premium'] else "Нет"}

🪙 Баланс • {user['balance']}
🎴 Карточки • {user['cards']}
🧩 Фрагменты • {user['fragments']}

🌳 Дерево • {user['tree']} см
"""
    await message.answer(text)
