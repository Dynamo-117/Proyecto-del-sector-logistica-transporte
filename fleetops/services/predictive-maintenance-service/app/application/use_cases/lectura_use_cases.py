from __future__ import annotations

from uuid import UUID

from app.application.ports.repositories import (
    AlertaRepository,
    EstadoMantenimientoRepository,
    LecturaOdometroRepository,
    VehiculoConocidoRepository,
)
from app.domain.entities import Alerta, LecturaOdometro, evaluar_tipos_a_alertar
from app.domain.exceptions import VehiculoDesconocido


class RegistrarLecturaOdometro:
    """Registra una lectura de kilometraje/horas de motor y evalua, contra los
    umbrales fijos de mantenimiento, si corresponde generar nuevas alertas
    (evitando duplicar una alerta de un tipo que ya este ACTIVA)."""

    def __init__(
        self,
        lectura_repo: LecturaOdometroRepository,
        vehiculo_repo: VehiculoConocidoRepository,
        estado_repo: EstadoMantenimientoRepository,
        alerta_repo: AlertaRepository,
    ):
        self._lectura_repo = lectura_repo
        self._vehiculo_repo = vehiculo_repo
        self._estado_repo = estado_repo
        self._alerta_repo = alerta_repo

    async def ejecutar(
        self, vehiculo_id: UUID, kilometraje_km: float, horas_motor: float
    ) -> tuple[LecturaOdometro, list[Alerta]]:
        if not await self._vehiculo_repo.existe(vehiculo_id):
            raise VehiculoDesconocido(
                f"Vehiculo '{vehiculo_id}' no esta registrado en predictive-maintenance-service"
            )

        lectura = await self._lectura_repo.guardar(
            LecturaOdometro(
                vehiculo_id=vehiculo_id, kilometraje_km=kilometraje_km, horas_motor=horas_motor
            )
        )

        estados = await self._estado_repo.obtener_todos(vehiculo_id)
        tipos_candidatos = evaluar_tipos_a_alertar(kilometraje_km, horas_motor, estados)

        nuevas_alertas = []
        for tipo in tipos_candidatos:
            if await self._alerta_repo.existe_activa(vehiculo_id, tipo):
                continue
            alerta = await self._alerta_repo.crear(
                Alerta(
                    vehiculo_id=vehiculo_id,
                    tipo=tipo,
                    kilometraje_km=kilometraje_km,
                    horas_motor=horas_motor,
                )
            )
            nuevas_alertas.append(alerta)

        return lectura, nuevas_alertas
