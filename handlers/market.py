from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(lambda m: m.text and m.text.lower().strip() in ["рынок", "/market", "🔄 рынок"])
async def market(message: Message):
    await message.answer("🔄 Рынок пока в разработке")
