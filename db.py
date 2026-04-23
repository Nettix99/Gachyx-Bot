import asyncpg
from config import DATABASE_URL

pool = None


async def connect():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)


async def get_connection():
    if pool is None:
        raise Exception("DB not initialized yet (pool is None)")
    return pool.acquire()


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


async def get_user(user_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE user_id=$1",
            user_id
        )
