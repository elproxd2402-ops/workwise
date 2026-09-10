from typing import Annotated
import os

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .ai_summary import generate_summary, utc_now
from .cv_ai import generar_cv, revisar_cv
from .db import db_session
from .models import Empresa, Oferta, Resena, SancionSunafil
from .schemas import EmpresaCard, EmpresaDetail, RebuildOut, CVRequest, CVResponse
from .scoring import calcular_puntaje, desglose_puntaje, haversine_km, mejor_oferta_referencia, semaforo

from .startup import initialize_database

app = FastAPI(title="WorkWise API", version="1.0.0")


@app.on_event("startup")
def startup_event():
    initialize_database()

origins = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def get_db():
    with db_session() as db:
        yield db


DB = Annotated[Session, Depends(get_db)]


def _avg_rating(e: Empresa) -> float:
    return sum(r.rating for r in e.resenas) / len(e.resenas) if e.resenas else 0


def card_from_empresa(e: Empresa, lat: float | None = None, lon: float | None = None) -> EmpresaCard:
    """Puntaje calculado dinámicamente a partir de reseñas/sanciones/ofertas
    actuales en la base de datos (punto 1: no depende de recalcular a mano).
    apto_joven/exige_titulo usan la MEJOR oferta de la empresa (punto 2), no un
    campo genérico de la empresa."""
    distancia = None
    if lat is not None and lon is not None and e.latitud is not None and e.longitud is not None:
        distancia = haversine_km(lat, lon, e.latitud, e.longitud)

    apto_joven, exige_titulo = mejor_oferta_referencia(e.ofertas)
    puntaje = calcular_puntaje(_avg_rating(e), len(e.sanciones), apto_joven, exige_titulo)

    return EmpresaCard(
        id=e.id,
        nombre=e.nombre,
        sector=e.sector,
        ciudad=e.ciudad,
        puntaje=puntaje,
        semaforo=semaforo(puntaje),
        resumen_ia=e.resumen_ia or "Todavía no hay un resumen disponible.",
        exige_titulo=exige_titulo,
        apto_joven=apto_joven,
        sanciones=len(e.sanciones),
        ofertas_cortas=sum(1 for o in e.ofertas if o.jornada_horas is not None and o.jornada_horas <= 6),
        distancia_km=distancia,
        es_demo=e.es_demo,
    )


@app.get("/health")
def health():
    return {"ok": True, "service": "workwise"}


@app.get("/empresas", response_model=list[EmpresaCard])
def list_empresas(
    db: DB,
    q: str | None = Query(default=None, max_length=120),
    sin_titulo: bool = False,
    jornada_corta: bool = False,
    cerca_de: str | None = Query(default=None, max_length=120),
    seguro: bool = False,
    ciudad: str | None = Query(default=None, max_length=120),
    lat: float | None = None,
    lon: float | None = None,
    limit: int = Query(default=40, ge=1, le=100),
):
    stmt = select(Empresa).options(selectinload(Empresa.resenas), selectinload(Empresa.sanciones), selectinload(Empresa.ofertas))
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where((Empresa.nombre.ilike(like)) | (Empresa.sector.ilike(like)))
    if sin_titulo:
        # "Sin título" debe reflejar si HAY una oferta concreta sin ese requisito
        # (punto 2 y 3), no un campo genérico de la empresa.
        stmt = stmt.where(Empresa.ofertas.any(Oferta.requiere_titulo.is_(False)))
    if seguro:
        stmt = stmt.where(~Empresa.sanciones.any())
    if ciudad:
        stmt = stmt.where(func.lower(Empresa.ciudad) == ciudad.lower())
    if cerca_de:
        stmt = stmt.where(func.lower(Empresa.ciudad).contains(cerca_de.lower()))

    empresas = list(db.scalars(stmt).all())
    if jornada_corta:
        empresas = [e for e in empresas if any(o.jornada_horas is not None and o.jornada_horas <= 6 for o in e.ofertas)]

    cards = [card_from_empresa(e, lat, lon) for e in empresas]
    if lat is not None and lon is not None:
        cards.sort(key=lambda x: x.distancia_km if x.distancia_km is not None else 10**9)
    else:
        cards.sort(key=lambda x: x.puntaje, reverse=True)
    return cards[:limit]


@app.get("/empresas/{empresa_id}", response_model=EmpresaDetail)
def get_empresa(empresa_id: int, db: DB):
    stmt = select(Empresa).where(Empresa.id == empresa_id).options(
        selectinload(Empresa.resenas),
        selectinload(Empresa.sanciones),
        selectinload(Empresa.ofertas),
    )
    e = db.scalar(stmt)
    if not e:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    apto_joven, exige_titulo = mejor_oferta_referencia(e.ofertas)
    desglose = desglose_puntaje(_avg_rating(e), len(e.sanciones), apto_joven, exige_titulo)
    return EmpresaDetail(
        **card_from_empresa(e).model_dump(),
        actualizado_ia=e.actualizado_ia,
        reputacion=desglose["reputacion"],
        cumplimiento=desglose["cumplimiento"],
        elegibilidad_juvenil=desglose["elegibilidad_juvenil"],
        facil_aplicar=desglose["facil_aplicar"],
        resenas=e.resenas,
        sanciones_detalle=e.sanciones,
        ofertas=e.ofertas,
    )


@app.post("/empresas/{empresa_id}/regenerar_resumen", response_model=RebuildOut)
def regenerate_summary(empresa_id: int, db: DB, x_admin_token: str | None = Header(default=None)):
    expected = os.getenv("ADMIN_TOKEN")
    if not expected or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Endpoint protegido. Usa X-Admin-Token.")
    stmt = select(Empresa).where(Empresa.id == empresa_id).options(selectinload(Empresa.resenas))
    e = db.scalar(stmt)
    if not e:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    try:
        e.resumen_ia = generate_summary(e)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    e.actualizado_ia = utc_now()
    db.flush()
    return RebuildOut(id=e.id, resumen_ia=e.resumen_ia, actualizado_ia=e.actualizado_ia)


@app.post("/ia/cv", response_model=CVResponse)
def asistente_cv(payload: CVRequest, request: Request):
    """Genera o corrige un CV. La clave de OpenAI permanece solo en el backend."""
    try:
        if payload.accion == "revisar":
            if not payload.texto_cv.strip():
                raise HTTPException(status_code=400, detail="Escribe o pega tu CV para revisarlo.")
            return revisar_cv(payload.texto_cv)
        if not payload.datos:
            raise HTTPException(status_code=400, detail="Completa al menos algunos datos para crear el CV.")
        return generar_cv(payload.datos)
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="No se pudo procesar el CV. Inténtalo nuevamente.")
