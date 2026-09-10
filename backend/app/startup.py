"""Inicialización idempotente para despliegues sencillos.

Crea el esquema y, solo si la BD está completamente vacía, carga los datos
ficticios de demostración. Nunca borra datos de una BD que ya tenga empresas.
"""
from pathlib import Path

from sqlalchemy import text

from .db import engine

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "sql" / "001_schema.sql"
SEED = ROOT / "sql" / "002_demo_seed.sql"


def initialize_database() -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql(SCHEMA.read_text(encoding="utf-8"))
        count = conn.execute(text("SELECT COUNT(*) FROM empresas")).scalar_one()
        if count == 0:
            conn.exec_driver_sql(SEED.read_text(encoding="utf-8"))
