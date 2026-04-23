from services.card_service import get_random_card
from database.queries import create_user

def register(dp):

    @dp.message_handler(lambda m: m.text.lower() == "карточка")
    async def card_handler(message):

        user_id = message.from_user.id

        create_user(user_id)

        card = get_random_card(user_id)

        await message.answer(
            f"🎴 Ты получил карточку!\n\n"
            f"{card['rarity']} {card['name']}\n\n"
            f"🍬 +{card['candies']}\n"
            f"🧩 +1"
        )
