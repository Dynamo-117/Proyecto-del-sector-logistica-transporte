from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class PlanRutaRequest(BaseModel):
    paradas: list[UUID] = Field(..., min_length=2, description="Nodos a visitar, en orden")


class ComponentePlanResponse(BaseModel):
    tipo: Literal["tramo", "trayecto"]
    nombre: str
    distancia_km: float
    cantidad_tramos: int
    hijos: list[ComponentePlanResponse] = []


class PlanRutaResponse(BaseModel):
    distancia_km: float
    cantidad_tramos: int
    paradas: list[str]
    nodos: list[UUID]
    estructura: ComponentePlanResponse
