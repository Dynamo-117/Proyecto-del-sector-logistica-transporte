"""Demostracion del patron FLYWEIGHT en predictive-maintenance-service.

Se crean 100 000 alertas en memoria de dos maneras y se mide cuanta memoria
ocupa cada una:
  - SIN Flyweight: cada alerta carga su propia copia del tipo de mantenimiento
    (nombre, descripcion, recomendacion, prioridad, umbrales), como ocurre cuando
    cada fila trae sus textos desde la base de datos.
  - CON Flyweight: todas las alertas apuntan al unico TipoMantenimiento que
    entrega la fabrica para su tipo (estado intrinseco compartido); cada alerta
    conserva solo lo suyo (vehiculo, kilometraje, horas).

Uso (desde services/predictive-maintenance-service, con el entorno virtual activo):
    python -m scripts.demo_flyweight
"""

import tracemalloc
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.entities import TipoAlerta
from app.domain.tipos_mantenimiento import (
    FabricaTiposMantenimiento,
    TipoMantenimiento,
)

CANTIDAD = 100_000
TIPOS = list(TipoAlerta)


@dataclass(slots=True)
class AlertaEnMemoria:
    """Estado extrinseco (propio de cada alerta) + referencia al tipo."""

    vehiculo_id: UUID
    kilometraje_km: float
    horas_motor: float
    tipo: TipoMantenimiento


def copia(texto: str) -> str:
    """Una copia nueva del texto (como al leerlo otra vez desde la base de datos)."""
    return (texto + " ")[:-1]


def copia_del_tipo(original: TipoMantenimiento) -> TipoMantenimiento:
    return TipoMantenimiento(
        tipo=original.tipo,
        nombre=copia(original.nombre),
        descripcion=copia(original.descripcion),
        recomendacion=copia(original.recomendacion),
        prioridad=copia(original.prioridad),
        intervalo_km=original.intervalo_km,
        intervalo_horas=original.intervalo_horas,
    )


def crear_sin_flyweight(modelo: FabricaTiposMantenimiento) -> list[AlertaEnMemoria]:
    return [
        AlertaEnMemoria(uuid4(), 10_000.0 + i, 300.0, copia_del_tipo(modelo.obtener(TIPOS[i % 2])))
        for i in range(CANTIDAD)
    ]


def crear_con_flyweight(fabrica: FabricaTiposMantenimiento) -> list[AlertaEnMemoria]:
    return [
        AlertaEnMemoria(uuid4(), 10_000.0 + i, 300.0, fabrica.obtener(TIPOS[i % 2]))
        for i in range(CANTIDAD)
    ]


def medir(crear) -> tuple[list[AlertaEnMemoria], float]:
    tracemalloc.start()
    alertas = crear()
    memoria_mb = tracemalloc.get_traced_memory()[0] / (1024 * 1024)
    tracemalloc.stop()
    return alertas, memoria_mb


def main() -> None:
    print("PATRON FLYWEIGHT -- predictive-maintenance-service\n")
    modelo = FabricaTiposMantenimiento()
    modelo.obtener(TIPOS[0])
    modelo.obtener(TIPOS[1])

    sin, mb_sin = medir(lambda: crear_sin_flyweight(modelo))
    objetos_sin = len({id(a.tipo) for a in sin})
    del sin

    fabrica = FabricaTiposMantenimiento()
    con, mb_con = medir(lambda: crear_con_flyweight(fabrica))
    objetos_con = len({id(a.tipo) for a in con})

    print(f"1) {CANTIDAD:,} alertas de {len(TIPOS)} tipos distintos, creadas de dos maneras:\n")
    print(f"   {'':<28}{'TipoMantenimiento':>20}{'Memoria':>12}")
    print(f"   {'':<28}{'distintos en memoria':>20}{'':>12}")
    print("   " + "-" * 60)
    print(f"   {'SIN Flyweight':<28}{objetos_sin:>20,}{mb_sin:>9.1f} MB")
    print(f"   {'CON Flyweight (fabrica)':<28}{objetos_con:>20,}{mb_con:>9.1f} MB")
    ahorro = (1 - mb_con / mb_sin) * 100
    print(f"\n   Ahorro de memoria: {ahorro:.0f} %", end="")
    print(f"   (la fabrica creo {fabrica.cantidad_creada} objetos)\n")

    print("2) Estado intrinseco (compartido) vs extrinseco (propio de cada alerta):")
    a, b = con[0], con[2]
    print(f"   alerta #0 y alerta #2 (mismo tipo) -> mismo objeto de tipo?  {a.tipo is b.tipo}")
    print(
        f"   alerta #0 y alerta #1 (tipo distinto) -> mismo objeto?        {a.tipo is con[1].tipo}"
    )
    print(
        f"   intrinseco (compartido): {a.tipo.nombre} | prioridad {a.tipo.prioridad}"
        f" | cada {a.tipo.intervalo_km:,.0f} km"
    )
    print(
        f"   extrinseco (propio):     vehiculo {str(a.vehiculo_id)[:8]}..."
        f" | {a.kilometraje_km:,.0f} km"
    )

    print(
        "\nRESULTADO: miles de alertas comparten solo un objeto por tipo en lugar de uno cada una."
    )


if __name__ == "__main__":
    main()
