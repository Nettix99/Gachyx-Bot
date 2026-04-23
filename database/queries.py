from database.db import cursor, conn


# 👤 создать пользователя
def create_user(user_id):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()


# 🍬 добавить конфеты
def add_candies(user_id, amount):
    cursor.execute(
        "UPDATE users SET candies = candies + ? WHERE user_id = ?",
        (amount, user_id)
    )
    conn.commit()


# 🧩 добавить фрагменты
def add_fragments(user_id, amount):
    cursor.execute(
        "UPDATE users SET fragments = fragments + ? WHERE user_id = ?",
        (amount, user_id)
    )
    conn.commit()


# 🎴 добавить карточку
def add_card(user_id, name, rarity):

    # проверяем есть ли уже
    cursor.execute(
        "SELECT count FROM cards WHERE user_id=? AND name=?",
        (user_id, name)
    )
    result = cursor.fetchone()

    if result:
        cursor.execute(
            "UPDATE cards SET count = count + 1 WHERE user_id=? AND name=?",
            (user_id, name)
        )
    else:
        cursor.execute(
            "INSERT INTO cards (user_id, name, rarity) VALUES (?, ?, ?)",
            (user_id, name, rarity)
        )

    conn.commit()
