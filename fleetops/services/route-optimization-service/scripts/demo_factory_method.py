"""Demostracion del patron FACTORY METHOD en route-optimization-service.

Muestra que cada Creadora concreta decide que repositorio fabricar, que el
codigo que las usa (obtener_repositorio) es identico para las 5, y que la
Creadora abstracta no se puede instanciar.

Uso (desde services/route-optimization-service, con el entorno virtual activo):
    python -m scripts.demo_factory_method
"""

from app.infrastructure.db.arista_repository import AristaRepositorioCreador
from app.infrastructure.db.carga_repository import CargaRepositorioCreador
from app.infrastructure.db.nodo_repository import NodoRepositorioCreador
from app.infrastructure.db.repositorio_creador import RepositorioCreador
from app.infrastructure.db.ruta_repository import RutaRepositorioCreador
from app.infrastructure.db.vehiculo_disponible_repository import (
    VehiculoDisponibleRepositorioCreador,
)


def main() -> None:
    print("PATRON FACTORY METHOD -- route-optimization-service\n")

    print("1) La Creadora abstracta NO se puede instanciar:")
    try:
        RepositorioCreador()
    except TypeError as error:
        print(f"   RepositorioCreador()  ->  TypeError: {error}\n")

    print("2) El mismo codigo cliente (obtener_repositorio) con 5 Creadoras distintas:")
    print(f"   {'CREADORA CONCRETA':<40}{'REPOSITORIO QUE FABRICA'}")
    print("   " + "-" * 82)
    creadoras: list[RepositorioCreador] = [
        NodoRepositorioCreador(),
        AristaRepositorioCreador(),
        CargaRepositorioCreador(),
        RutaRepositorioCreador(),
        VehiculoDisponibleRepositorioCreador(),
    ]
    sesion_de_prueba = object()
    for creadora in creadoras:
        repo = creadora.obtener_repositorio(sesion_de_prueba)
        print(f"   {type(creadora).__name__:<40}{type(repo).__name__}")

    print("\nRESULTADO: 5 Creadoras concretas -> 5 repositorios distintos, un solo metodo de uso.")


if __name__ == "__main__":
    main()
