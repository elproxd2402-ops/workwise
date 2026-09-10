from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ResenaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    texto: str
    rating: int = Field(ge=1, le=5)
    fecha: date | None = None
    fuente: str | None = None
    url_fuente: str | None = None


class SancionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: str
    fecha: date | None = None
    fuente: str | None = None
    url_fuente: str | None = None


class OfertaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo_puesto: str
    descripcion: str | None = None
    requiere_titulo: bool
    jornada_horas: float | None = None
    apto_joven: bool
    alertas: str | None = None
    url_aplicacion: str | None = None


class EmpresaCard(BaseModel):
    id: int
    nombre: str
    sector: str | None
    ciudad: str | None
    puntaje: float
    semaforo: str
    resumen_ia: str
    exige_titulo: bool
    apto_joven: bool
    sanciones: int
    ofertas_cortas: int
    distancia_km: float | None = None
    es_demo: bool = False


class EmpresaDetail(EmpresaCard):
    actualizado_ia: datetime | None = None
    reputacion: float
    cumplimiento: int
    elegibilidad_juvenil: int
    facil_aplicar: int
    resenas: list[ResenaOut]
    sanciones_detalle: list[SancionOut]
    ofertas: list[OfertaOut]


class RebuildOut(BaseModel):
    id: int
    resumen_ia: str
    actualizado_ia: datetime


class CVRequest(BaseModel):
    accion: str = Field(pattern="^(generar|revisar)$")
    datos: dict[str, str] = Field(default_factory=dict)
    texto_cv: str = Field(default="", max_length=12000)


class CVResponse(BaseModel):
    cv: str
    correcciones: list[str]
    fortalezas: list[str]
    faltantes: list[str]
