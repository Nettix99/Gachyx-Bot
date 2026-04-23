from aiogram import Router
from aiogram.types import Message
from db import pool

router = Router()

@router.message(lambda m: m.text and m.text.lower().strip() in ["полить", "/water", "💧 полить"])
async def water(message: Message):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET tree = tree + 1 WHERE user_id=$1",
            message.from_user.id
        )

    await message.answer("💧 Ты полил дерево! +1 см")
