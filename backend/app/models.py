from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Empresa(Base):
    __tablename__ = "empresas"
    __table_args__ = (
        CheckConstraint("puntaje >= 0 AND puntaje <= 100", name="ck_empresas_puntaje"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    sector: Mapped[str | None] = mapped_column(String(120))
    ciudad: Mapped[str | None] = mapped_column(String(120), index=True)
    exige_titulo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    apto_joven: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    resumen_ia: Mapped[str | None] = mapped_column(Text)
    puntaje: Mapped[float] = mapped_column(Float, default=0, nullable=False, index=True)
    semaforo: Mapped[str] = mapped_column(String(10), default="rojo", nullable=False)
    actualizado_ia: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    latitud: Mapped[float | None] = mapped_column(Float)
    longitud: Mapped[float | None] = mapped_column(Float)
    web_aplicacion: Mapped[str | None] = mapped_column(String(500))
    es_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default="false")

    resenas: Mapped[list["Resena"]] = relationship(back_populates="empresa", cascade="all, delete-orphan")
    sanciones: Mapped[list["SancionSunafil"]] = relationship(back_populates="empresa", cascade="all, delete-orphan")
    ofertas: Mapped[list["Oferta"]] = relationship(back_populates="empresa", cascade="all, delete-orphan")


class Resena(Base):
    __tablename__ = "resenas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[date | None] = mapped_column(Date)
    fuente: Mapped[str | None] = mapped_column(String(80))
    url_fuente: Mapped[str | None] = mapped_column(String(500))

    empresa: Mapped[Empresa] = relationship(back_populates="resenas")


class SancionSunafil(Base):
    __tablename__ = "sanciones_sunafil"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(200), nullable=False)
    fecha: Mapped[date | None] = mapped_column(Date)
    fuente: Mapped[str | None] = mapped_column(String(120))
    url_fuente: Mapped[str | None] = mapped_column(String(500))

    empresa: Mapped[Empresa] = relationship(back_populates="sanciones")


class Oferta(Base):
    __tablename__ = "ofertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False, index=True)
    titulo_puesto: Mapped[str] = mapped_column(String(180), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    requiere_titulo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    jornada_horas: Mapped[float | None] = mapped_column(Float)
    apto_joven: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alertas: Mapped[str | None] = mapped_column(Text)
    url_aplicacion: Mapped[str | None] = mapped_column(String(500))

    empresa: Mapped[Empresa] = relationship(back_populates="ofertas")
