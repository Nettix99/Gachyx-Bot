
from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(lambda m: m.text and m.text.lower().strip() in ["бонус", "/bonus"])
async def bonus(message: Message):
    await message.answer("🎁 Бонус пока в разработке")
