import asyncio
import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect(
            user='hitchhike',
            password='hitchhike',
            database='hitchhike_db',
            host='localhost',
            port=5432
        )
        print("✅ Successfully connected to PostgreSQL!")
        version = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version: {version}")
        await conn.close()
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
