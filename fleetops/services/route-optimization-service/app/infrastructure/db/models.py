import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.infrastructure.db.guid import GUID


class Base(DeclarativeBase):
    pass


class NodoModel(Base):
    __tablename__ = "nodos"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)


class AristaModel(Base):
    __tablename__ = "aristas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    nodo_origen_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("nodos.id"), nullable=False
    )
    nodo_destino_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("nodos.id"), nullable=False
    )
    distancia_km: Mapped[float] = mapped_column(Float, nullable=False)


class CargaModel(Base):
    __tablename__ = "cargas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    origen_nodo_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("nodos.id"), nullable=False
    )
    destino_nodo_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("nodos.id"), nullable=False
    )
    peso_kg: Mapped[float] = mapped_column(Float, nullable=False)
    volumen_m3: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RutaModel(Base):
    __tablename__ = "rutas"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    carga_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("cargas.id"), nullable=False)
    vehiculo_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    nodos: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    distancia_km: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class VehiculoDisponibleModel(Base):
    __tablename__ = "vehiculos_disponibles"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True)
    placa: Mapped[str] = mapped_column(String(20), nullable=False)
    capacidad_kg: Mapped[float] = mapped_column(Float, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
