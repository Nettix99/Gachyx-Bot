import random
from database.queries import add_card, add_candies, add_fragments

RARITIES = {
    "⚪": 50,
    "🟢": 25,
    "🔵": 15,
    "🟣": 7,
    "🟡": 2.5,
    "🔴": 0.5
}

CARDS = {
    "⚪": ["Саконжи Урокодаки"],
    "🟢": ["Канао Цуюри"],
    "🔵": ["Синобу Кочо"],
    "🟣": ["Незуко Камадо", "Гию Томиока"],
    "🟡": ["Танджиро"],
    "🔴": ["Кокушибо"]
}


def get_random_card(user_id):

    rarity = random.choices(
        list(RARITIES.keys()),
        weights=list(RARITIES.values())
    )[0]

    name = random.choice(CARDS[rarity])

    # 💰 награда
    rewards = {
        "⚪": (10, 30),
        "🟢": (30, 60),
        "🔵": (60, 120),
        "🟣": (120, 250),
        "🟡": (250, 500),
        "🔴": (500, 1000)
    }

    candies = random.randint(*rewards[rarity])

    # 📦 сохраняем
    add_card(user_id, name, rarity)
    add_candies(user_id, candies)
    add_fragments(user_id, 1)

    return {
        "rarity": rarity,
        "name": name,
        "candies": candies
    }
