"""Demostracion del patron ADAPTER en navigation-integration-service.

Dos proveedores con APIs completamente distintas (OSRM y Valhalla) se usan a
traves de la misma interfaz NavigationProvider y del mismo caso de uso
CalcularRuta. Ademas muestra lo que el adaptador esconde: la respuesta cruda de
Valhalla (otras claves, otras unidades, geometria codificada).

Requiere internet (consulta los servidores publicos de OSRM y Valhalla).

Uso (desde services/navigation-integration-service, con el entorno virtual activo):
    python -m scripts.demo_adapter
"""

import asyncio

from app.application.use_cases.ruta_use_cases import CalcularRuta
from app.core.config import get_settings
from app.domain.entities import Coordenada
from app.infrastructure.external.osrm_client import OSRMClient
from app.infrastructure.external.valhalla_adapter import ValhallaNavigationAdapter
from app.infrastructure.external.valhalla_api import ValhallaApi

BOGOTA = Coordenada(latitud=4.7110, longitud=-74.0721)
MEDELLIN = Coordenada(latitud=6.2442, longitud=-75.5812)


async def main() -> None:
    print("PATRON ADAPTER -- navigation-integration-service\n")

    api = ValhallaApi()
    print("1) El Adaptado (ValhallaApi) habla su propio idioma - respuesta cruda de Valhalla:")
    try:
        viaje = await api.obtener_viaje(
            BOGOTA.latitud, BOGOTA.longitud, MEDELLIN.latitud, MEDELLIN.longitud
        )
    except Exception as error:
        print(f"   No se pudo consultar Valhalla ({type(error).__name__}): {error}")
        await api.cerrar()
        return
    resumen = viaje["summary"]
    shape = viaje["legs"][0]["shape"]
    print(f"   trip.summary.length = {resumen['length']}        (kilometros)")
    print(f"   trip.summary.time   = {resumen['time']}   (segundos)")
    print(f"   trip.legs[0].shape  = '{shape[:36]}...'  ({len(shape)} caracteres, polyline6)\n")

    print("2) El mismo caso de uso (CalcularRuta) con dos proveedores distintos:")
    proveedores = {
        "OSRM (OSRMClient)": OSRMClient(get_settings().osrm_base_url),
        "Valhalla (ValhallaNavigationAdapter)": ValhallaNavigationAdapter(api),
    }
    print(f"   {'PROVEEDOR':<40}{'DISTANCIA':>11}{'DURACION':>12}{'PUNTOS':>9}   TIPO DEVUELTO")
    print("   " + "-" * 88)
    for nombre, proveedor in proveedores.items():
        try:
            ruta = await CalcularRuta(proveedor).ejecutar(BOGOTA, MEDELLIN)
        except Exception as error:
            print(f"   {nombre:<40}ERROR: {type(error).__name__}")
            continue
        print(
            f"   {nombre:<40}{ruta.distancia_km:>8.1f} km{ruta.duracion_min:>9.1f} min"
            f"{len(ruta.puntos):>9}   {type(ruta).__name__}"
        )
    for proveedor in proveedores.values():
        await proveedor.cerrar()

    print(
        "\nRESULTADO: dos APIs incompatibles, una sola interfaz y un solo tipo de respuesta (Ruta)."
    )


if __name__ == "__main__":
    asyncio.run(main())
