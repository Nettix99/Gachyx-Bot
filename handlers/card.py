import random
import json

from aiogram import Router
from aiogram.types import Message
from db import pool

from cards_db import CARDS  # файл с твоими картами

router = Router()


@router.message(lambda m: m.text and m.text.lower().strip() in ["карта", "/card", "🎴 карта"])
async def card(message: Message):
    card = random.choice(CARDS)

    new_card = {
        "name": card["name"],
        "rarity": card["rarity"],
        "price": card["price"]
    }

    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT cards_json FROM users WHERE user_id=$1",
            message.from_user.id
        )

        cards = json.loads(user["cards_json"]) if user["cards_json"] else []

        cards.append(new_card)

        await conn.execute(
            "UPDATE users SET cards_json=$1 WHERE user_id=$2",
            json.dumps(cards),
            message.from_user.id
        )

        await conn.execute(
            "UPDATE users SET cards = cards + 1 WHERE user_id=$1",
            message.from_user.id
        )

    await message.answer(
        f"🎴 Новая карта!\n\n"
        f"🏷 {card['name']}\n"
        f"⭐ {card['rarity']}\n"
        f"💰 {card['price']}\n\n"
        f"📝 {card['desc']}"
    )
