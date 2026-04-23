from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(lambda m: m.text and m.text.lower().strip() in ["помощь", "/help", "❓ помощь"])
async def help_cmd(message: Message):
    await message.answer("""
📖 Команды:

📁 профиль
🎴 карта
📦 карты
🔄 рынок
🎁 бонус
🌳 дерево
💧 полить
❓ помощь
""")
