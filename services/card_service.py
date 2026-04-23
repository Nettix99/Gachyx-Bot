import random

RARITIES = {
    "⚪": 50,
    "🟢": 25,
    "🔵": 15,
    "🟣": 7,
    "🟡": 2.5,
    "🔴": 0.5
}

CARDS = {
    "🔴": ["Кокушибо", "Музан", "Акадза"],
    "🟡": ["Ренгоку", "Муичиро"],
    "🟣": ["Незуко", "Тенген"],
    "🔵": ["Гию", "Синобу"],
    "🟢": ["Канао"],
    "⚪": ["Мурата"]
}


def get_random_card(user_id):

    rarity = random.choices(
        list(RARITIES.keys()),
        weights=list(RARITIES.values())
    )[0]

    name = random.choice(CARDS[rarity])

    return {
        "rarity": rarity,
        "name": name
    }
