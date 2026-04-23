from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(lambda msg: msg.text.lower() in ["помощь", "/help"])
async def help_cmd(message: Message):
    await message.answer("""
📖 Команды:

профиль / profile
карта / card
карты / inventory
рынок / market
бонус / bonus
дерево / tree
полить / water
топ / top
""")
