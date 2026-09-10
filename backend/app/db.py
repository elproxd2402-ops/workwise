import os
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator

load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


def build_database_url() -> str:
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        # Railway often exposes postgres://; SQLAlchemy expects postgresql+psycopg2://.
        if explicit.startswith("postgres://"):
            explicit = explicit.replace("postgres://", "postgresql+psycopg2://", 1)
        elif explicit.startswith("postgresql://"):
            explicit = explicit.replace("postgresql://", "postgresql+psycopg2://", 1)
        return explicit

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    name = os.getenv("DB_NAME", "workwise")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


_url = build_database_url()
import re as _re
print(">>> URL DE CONEXION USADA:", _re.sub(r':([^:@]+)@', ':***@', _url))
engine = create_engine(_url, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@contextmanager
def db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
