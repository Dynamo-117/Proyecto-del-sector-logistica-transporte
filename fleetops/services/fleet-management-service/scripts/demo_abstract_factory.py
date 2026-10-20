"""Demostracion del patron ABSTRACT FACTORY en fleet-management-service.

Una misma funcion arma "la familia de persistencia" (Vehiculo + Conductor +
Usuario) a partir de una fabrica abstracta; solo cambia QUE fabrica concreta
se le pasa: la real (SQLAlchemy/PostgreSQL) o la de pruebas (en memoria).

Uso (desde services/fleet-management-service, con el entorno virtual activo):
    python -m scripts.demo_abstract_factory
"""

from app.infrastructure.db.repositorio_factory import (
    RepositorioFactory,
    SqlAlchemyRepositorioFactory,
)
from tests.unit.fakes import FakeRepositorioFactory


def armar_familia(fabrica: RepositorioFactory, sesion: object) -> dict[str, str]:
    return {
        "vehiculo": type(fabrica.crear_vehiculo_repo(sesion)).__name__,
        "conductor": type(fabrica.crear_conductor_repo(sesion)).__name__,
        "usuario": type(fabrica.crear_usuario_repo(sesion)).__name__,
    }


def main() -> None:
    print("PATRON ABSTRACT FACTORY -- fleet-management-service\n")

    print("1) La Fabrica abstracta NO se puede instanciar:")
    try:
        RepositorioFactory()
    except TypeError as error:
        print(f"   RepositorioFactory()  ->  TypeError: {error}\n")

    print("2) La misma funcion armar_familia(fabrica) con dos fabricas concretas:")
    for fabrica in (SqlAlchemyRepositorioFactory(), FakeRepositorioFactory()):
        print(f"\n   Fabrica concreta: {type(fabrica).__name__}")
        for producto, clase in armar_familia(fabrica, object()).items():
            print(f"      crear_{producto}_repo()  ->  {clase}")

    print("\nRESULTADO: cada fabrica produce una familia completa y coherente (nunca se mezclan).")


if __name__ == "__main__":
    main()
