from aiogram import Router
from aiogram.types import Message
from db import pool

router = Router()

@router.message(lambda m: m.text and m.text.lower().strip() in ["карта", "/card", "🎴 карта"])
async def card(message: Message):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET cards = cards + 1 WHERE user_id=$1",
            message.from_user.id
        )

    await message.answer("🎴 Ты получил карту!")
