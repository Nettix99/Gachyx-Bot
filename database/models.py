from database.db import cursor, conn


def create_tables():

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        candies INTEGER DEFAULT 0,
        fragments INTEGER DEFAULT 0,
        premium INTEGER DEFAULT 0,
        active_card TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        rarity TEXT,
        count INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cooldowns (
        user_id INTEGER,
        type TEXT,
        time INTEGER
    )
    """)

    conn.commit()
