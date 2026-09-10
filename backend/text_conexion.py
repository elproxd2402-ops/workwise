import anyio
from sqlalchemy import text
from app.db import engine

def worker():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("RESULTADO:", result.fetchone())

async def main():
    try:
        await anyio.to_thread.run_sync(worker)
        print("EXITO CON ANYIO")
    except Exception as e:
        print("FALLO CON ANYIO:", repr(e))

anyio.run(main)