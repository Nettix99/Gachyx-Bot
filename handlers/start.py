def register(dp):

    @dp.message_handler(commands=["start"])
    async def start_handler(message):
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "Собирай карточки 🎴\n"
            "Зарабатывай 🍬\n"
        )
