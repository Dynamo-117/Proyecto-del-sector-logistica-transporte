"""Demostracion del patron COMPOSITE en route-optimization-service.

Un itinerario con varias paradas es un arbol: Itinerario -> Trayectos -> Tramos.
Las hojas (Tramo) y los compuestos (Trayecto) comparten la interfaz
ComponenteRuta, asi que se les pide distancia, cantidad de tramos y recorrido
exactamente igual sin importar su nivel.

Uso (desde services/route-optimization-service, con el entorno virtual activo):
    python -m scripts.demo_composite
"""

import asyncio

from app.application.use_cases.plan_use_cases import PlanificarRutaConParadas
from app.domain.entities import Arista, Nodo
from app.domain.itinerario import ComponenteRuta
from tests.unit.fakes import FakeAristaRepository, FakeNodoRepository


def imprimir_arbol(arbol: dict, nivel: int = 0) -> None:
    marca = "[trayecto]" if arbol["tipo"] == "trayecto" else "[tramo]   "
    print(f"   {'    ' * nivel}{marca} {arbol['nombre']:<30} {arbol['distancia_km']:>6.0f} km")
    for hijo in arbol["hijos"]:
        imprimir_arbol(hijo, nivel + 1)


async def main() -> None:
    print("PATRON COMPOSITE -- route-optimization-service\n")

    nodos, aristas = FakeNodoRepository(), FakeAristaRepository()
    ids = {}
    for nombre, lat, lon in (
        ("Bogota", 4.711, -74.072),
        ("Tunja", 5.535, -73.368),
        ("Bucaramanga", 7.119, -73.123),
        ("Medellin", 6.244, -75.581),
    ):
        ids[nombre] = (await nodos.crear(Nodo(nombre=nombre, latitud=lat, longitud=lon))).id
    for origen, destino, km in (
        ("Bogota", "Tunja", 150),
        ("Tunja", "Bucaramanga", 280),
        ("Bucaramanga", "Medellin", 400),
        ("Bogota", "Medellin", 415),
    ):
        await aristas.crear(
            Arista(nodo_origen_id=ids[origen], nodo_destino_id=ids[destino], distancia_km=km)
        )

    print("1) Plan con paradas: Bogota -> Bucaramanga -> Medellin  (arbol resultante)")
    caso = PlanificarRutaConParadas(nodos, aristas)
    itinerario, nombres = await caso.ejecutar([ids["Bogota"], ids["Bucaramanga"], ids["Medellin"]])
    imprimir_arbol(itinerario.describir(nombres))

    print("\n2) La misma interfaz (ComponenteRuta) en los tres niveles del arbol:")
    primer_trayecto = itinerario.hijos[0]
    primer_tramo = primer_trayecto.hijos[0]
    print(f"   {'NIVEL':<22}{'distancia_km()':>16}{'cantidad_tramos()':>20}")
    print("   " + "-" * 58)
    for etiqueta, componente in (
        ("Tramo (hoja)", primer_tramo),
        ("Trayecto (compuesto)", primer_trayecto),
        ("Itinerario (compuesto)", itinerario),
    ):
        assert isinstance(componente, ComponenteRuta)
        print(
            f"   {etiqueta:<22}{componente.distancia_km():>13.0f} km"
            f"{componente.cantidad_tramos():>20}"
        )

    recorrido = " -> ".join(nombres[n] for n in itinerario.nodos())
    print(f"\n3) Recorrido completo (nodos()): {recorrido}")
    print(
        f"\nRESULTADO: {itinerario.distancia_km():.0f} km en {itinerario.cantidad_tramos()} tramos,"
        " calculados recursivamente sin distinguir hojas de compuestos."
    )


if __name__ == "__main__":
    asyncio.run(main())
