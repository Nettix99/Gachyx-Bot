from services.card_service import get_random_card

def register(dp):

    @dp.message_handler(lambda m: m.text.lower() == "карточка")
    async def card_handler(message):

        user_id = message.from_user.id

        card = get_random_card(user_id)

        await message.answer(
            f"🎴 Ты получил карточку!\n\n"
            f"{card['rarity']} {card['name']}"
        )
