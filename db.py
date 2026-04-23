import asyncpg
from config import DATABASE_URL

pool: asyncpg.Pool | None = None


async def connect():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    print("✅ DB POOL CREATED")


async def create_tables():
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            balance INT DEFAULT 0,
            cards INT DEFAULT 0,
            fragments INT DEFAULT 0,
            tree INT DEFAULT 0,
            premium BOOLEAN DEFAULT FALSE,
            cards_json TEXT DEFAULT '[]'
        );
        """)


async def get_user(user_id: int):
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE user_id=$1",
            user_id
        )
        return user


async def create_user(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users(user_id)
        VALUES($1)
        ON CONFLICT DO NOTHING
        """, user_id)
