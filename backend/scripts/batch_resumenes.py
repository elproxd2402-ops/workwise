"""Genera resúmenes IA para empresas que todavía no tienen resumen.

Uso desde backend/:
    python -m scripts.batch_resumenes
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.ai_summary import generate_summary, utc_now
from app.db import db_session
from app.models import Empresa


def main() -> None:
    updated = 0
    skipped = 0
    failed = 0
    with db_session() as db:
        empresas = db.scalars(
            select(Empresa)
            .where(Empresa.resumen_ia.is_(None))
            .options(selectinload(Empresa.resenas))
            .order_by(Empresa.id)
        ).all()
        for empresa in empresas:
            try:
                empresa.resumen_ia = generate_summary(empresa)
                empresa.actualizado_ia = utc_now()
                db.flush()
                updated += 1
                print(f"OK  {empresa.id}: {empresa.nombre}")
            except Exception as exc:  # noqa: BLE001
                failed += 1
                print(f"ERR {empresa.id}: {empresa.nombre}: {exc}")
        skipped = 0
    print(f"Listo. actualizadas={updated}, errores={failed}, omitidas={skipped}")


if __name__ == "__main__":
    main()
