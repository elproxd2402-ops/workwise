"""Importador JSON local para fuentes autorizadas/API/CSV ya procesados.

Formato del JSON: lista de objetos con company + reviews + sanctions + offers.
El importador NO hace scraping directo: úsalo con datos que tengas derecho a usar.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import delete, select

from app.db import db_session
from app.models import Empresa, Oferta, Resena, SancionSunafil
from app.scoring import calcular_puntaje, mejor_oferta_referencia, semaforo


def upsert_company(db, item: dict) -> Empresa:
    data = item["empresa"]
    empresa = db.scalar(select(Empresa).where(Empresa.nombre == data["nombre"]))
    if not empresa:
        empresa = Empresa(nombre=data["nombre"])
        db.add(empresa)
    for key in ["sector", "ciudad", "exige_titulo", "apto_joven", "latitud", "longitud", "web_aplicacion"]:
        if key in data:
            setattr(empresa, key, data[key])
    return empresa


def main(path: str) -> None:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    with db_session() as db:
        for item in payload:
            empresa = upsert_company(db, item)
            db.flush()
            # El JSON se trata como un snapshot de la empresa: reemplazamos sus
            # reseñas/sanciones/ofertas para no duplicarlas si vuelves a importar
            # la misma fuente.
            db.execute(delete(Resena).where(Resena.empresa_id == empresa.id))
            db.execute(delete(SancionSunafil).where(SancionSunafil.empresa_id == empresa.id))
            db.execute(delete(Oferta).where(Oferta.empresa_id == empresa.id))

            for r in item.get("resenas", []):
                db.add(Resena(empresa_id=empresa.id, texto=r["texto"], rating=r["rating"], fecha=r.get("fecha"), fuente=r.get("fuente"), url_fuente=r.get("url_fuente")))
            for s in item.get("sanciones", []):
                db.add(SancionSunafil(empresa_id=empresa.id, tipo=s["tipo"], fecha=s.get("fecha"), fuente=s.get("fuente"), url_fuente=s.get("url_fuente")))
            for o in item.get("ofertas", []):
                jornada = o.get("jornada_horas")
                apto = bool(o.get("apto_joven", True)) and (jornada is not None and float(jornada) <= 6)
                db.add(Oferta(empresa_id=empresa.id, titulo_puesto=o["titulo_puesto"], descripcion=o.get("descripcion"), requiere_titulo=o.get("requiere_titulo", False), jornada_horas=jornada, apto_joven=apto, alertas=o.get("alertas"), url_aplicacion=o.get("url_aplicacion")))
            db.flush()
            ratings = db.query(Resena).filter(Resena.empresa_id == empresa.id).all()
            sanctions = db.query(SancionSunafil).filter(SancionSunafil.empresa_id == empresa.id).count()
            ofertas = db.query(Oferta).filter(Oferta.empresa_id == empresa.id).all()
            avg = sum(x.rating for x in ratings) / len(ratings) if ratings else 0
            apto_joven, exige_titulo = mejor_oferta_referencia(ofertas)
            empresa.puntaje = calcular_puntaje(avg, sanctions, apto_joven, exige_titulo)
            empresa.semaforo = semaforo(empresa.puntaje)
    print(f"Importación completa: {len(payload)} empresas.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python -m scripts.import_data ruta/al/datos.json")
    main(sys.argv[1])
