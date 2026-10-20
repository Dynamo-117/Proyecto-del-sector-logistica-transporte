from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities import UMBRALES_MANTENIMIENTO, TipoAlerta


@dataclass(frozen=True)
class TipoMantenimiento:
    # =================   PATRON GOF: FLYWEIGHT (Peso ligero) -- inicia aqui =================
    """El Peso ligero (Flyweight): el estado INTRINSECO de un tipo de
    mantenimiento -- lo que es igual para todas las alertas de ese tipo: su
    nombre, descripcion, recomendacion, prioridad y umbrales. Es inmutable
    (frozen), por eso puede compartirse con seguridad entre miles de alertas.

    El estado EXTRINSECO (a que vehiculo corresponde, con cuantos km, cuando)
    NO vive aqui: sigue en cada Alerta, que solo apunta a este objeto.
    """

    tipo: TipoAlerta
    nombre: str
    descripcion: str
    recomendacion: str
    prioridad: str
    intervalo_km: float
    intervalo_horas: float

    # ================= PATRON GOF: FLYWEIGHT (Peso ligero) -- termina aqui =================


_CATALOGO: dict[TipoAlerta, tuple[str, str, str, str]] = {
    TipoAlerta.CAMBIO_ACEITE: (
        "Cambio de aceite",
        "Se cumplio el intervalo de uso del motor desde el ultimo cambio de aceite y filtro, "
        "por lo que el lubricante pierde sus propiedades y aumenta el desgaste interno.",
        "Programar el cambio de aceite y del filtro en el taller antes de continuar con "
        "rutas largas; verificar el nivel y la presion de aceite despues del servicio.",
        "MEDIA",
    ),
    TipoAlerta.REVISION_GENERAL: (
        "Revision general",
        "Se cumplio el intervalo de la revision completa del vehiculo: frenos, suspension, "
        "direccion, luces, neumaticos, correas y sistemas de seguridad.",
        "Retirar el vehiculo de la operacion y realizar la revision general completa con "
        "lista de chequeo; no asignarle cargas nuevas hasta tener el informe tecnico.",
        "ALTA",
    ),
}


class FabricaTiposMantenimiento:
    # =================   PATRON GOF: FLYWEIGHT (Fabrica) -- inicia aqui =================
    """La Fabrica de pesos ligeros: guarda un unico TipoMantenimiento por tipo
    y lo entrega siempre que se le pide. Quien necesite el estado compartido
    NUNCA hace TipoMantenimiento(...) por su cuenta: pasa por obtener(), que
    crea el objeto la primera vez y reutiliza el mismo despues.
    """

    def __init__(self) -> None:
        self._pool: dict[TipoAlerta, TipoMantenimiento] = {}

    def obtener(self, tipo: TipoAlerta) -> TipoMantenimiento:
        existente = self._pool.get(tipo)
        if existente is not None:
            return existente

        nombre, descripcion, recomendacion, prioridad = _CATALOGO[tipo]
        umbral = UMBRALES_MANTENIMIENTO[tipo]
        creado = TipoMantenimiento(
            tipo=tipo,
            nombre=nombre,
            descripcion=descripcion,
            recomendacion=recomendacion,
            prioridad=prioridad,
            intervalo_km=umbral.intervalo_km,
            intervalo_horas=umbral.intervalo_horas,
        )
        self._pool[tipo] = creado
        return creado

    @property
    def cantidad_creada(self) -> int:
        return len(self._pool)

    # ================= PATRON GOF: FLYWEIGHT (Fabrica) -- termina aqui =================


FABRICA_TIPOS = FabricaTiposMantenimiento()
