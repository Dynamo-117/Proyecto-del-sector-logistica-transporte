"""Demostracion del patron BUILDER en navigation-integration-service.

  1) Construccion paso a paso de una Ruta con RutaBuilder (interfaz fluida).
  2) Validacion: construir() falla si falta un paso obligatorio.
  3) Flujo real: OSRMClient -> RutaDirector -> RutaBuilder -> Ruta, con una
     consulta REAL al servidor publico de OSRM (requiere internet).

Uso (desde services/navigation-integration-service, con el entorno virtual activo):
    python -m scripts.demo_builder
"""

import asyncio

from app.core.config import get_settings
from app.domain.entities import Coordenada
from app.domain.ruta_builder import RutaBuilder
from app.infrastructure.external.osrm_client import OSRMClient

BOGOTA = Coordenada(latitud=4.7110, longitud=-74.0721)
MEDELLIN = Coordenada(latitud=6.2442, longitud=-75.5812)


def paso_a_paso() -> None:
    print("1) RutaBuilder paso a paso (datos crudos: metros y segundos, geometria lon/lat):")
    builder = RutaBuilder()
    print("   RutaBuilder()")
    builder.con_extremos(BOGOTA, MEDELLIN)
    print("     .con_extremos(BOGOTA, MEDELLIN)")
    builder.con_metricas(distancia_metros=415000.0, duracion_segundos=18000.0)
    print("     .con_metricas(distancia_metros=415000.0, duracion_segundos=18000.0)")
    builder.con_geometria([(-74.0721, 4.7110), (-75.5812, 6.2442)])
    print("     .con_geometria([(-74.0721, 4.7110), (-75.5812, 6.2442)])")
    ruta = builder.construir()
    print("     .construir()")
    print(
        f"   -> distancia_km={ruta.distancia_km}  duracion_min={ruta.duracion_min}"
        f"  puntos={len(ruta.puntos)}\n"
    )


def validacion() -> None:
    print("2) construir() sin los pasos obligatorios:")
    for etiqueta, builder in (
        ("sin extremos", RutaBuilder().con_metricas(distancia_metros=1.0, duracion_segundos=1.0)),
        ("sin metricas", RutaBuilder().con_extremos(BOGOTA, MEDELLIN)),
    ):
        try:
            builder.construir()
        except ValueError as error:
            print(f"   {etiqueta:<13} ->  ValueError: {error}")
    print()


async def flujo_real() -> None:
    print("3) Flujo real contra OSRM: OSRMClient -> RutaDirector -> RutaBuilder -> Ruta")
    cliente = OSRMClient(get_settings().osrm_base_url)
    try:
        ruta = await cliente.calcular_ruta(BOGOTA, MEDELLIN)
        print("   Origen : Bogota    (4.7110, -74.0721)")
        print("   Destino: Medellin  (6.2442, -75.5812)")
        print(f"   distancia_km = {ruta.distancia_km:.1f}")
        print(f"   duracion_min = {ruta.duracion_min:.1f}  (~{ruta.duracion_min / 60:.1f} h)")
        print(f"   puntos       = {len(ruta.puntos)} coordenadas en la geometria")
        print(f"   primer punto = {ruta.puntos[0]}")
        print(f"   ultimo punto = {ruta.puntos[-1]}")
    except Exception as error:  # sin internet / OSRM caido
        print(f"   No se pudo consultar OSRM ({type(error).__name__}): {error}")
    finally:
        await cliente.cerrar()


def main() -> None:
    print("PATRON BUILDER -- navigation-integration-service\n")
    paso_a_paso()
    validacion()
    asyncio.run(flujo_real())
    print("\nRESULTADO: la Ruta se ensambla paso a paso; el cliente HTTP ya no hace conversiones.")


if __name__ == "__main__":
    main()
