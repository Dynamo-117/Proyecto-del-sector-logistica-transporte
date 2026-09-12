import pytest

from app.infrastructure.db.arista_repository import (
    AristaRepositorioCreador,
    SqlAlchemyAristaRepository,
)
from app.infrastructure.db.carga_repository import (
    CargaRepositorioCreador,
    SqlAlchemyCargaRepository,
)
from app.infrastructure.db.nodo_repository import NodoRepositorioCreador, SqlAlchemyNodoRepository
from app.infrastructure.db.repositorio_creador import RepositorioCreador
from app.infrastructure.db.ruta_repository import RutaRepositorioCreador, SqlAlchemyRutaRepository
from app.infrastructure.db.vehiculo_disponible_repository import (
    SqlAlchemyVehiculoDisponibleRepository,
    VehiculoDisponibleRepositorioCreador,
)


def test_no_se_puede_instanciar_la_creadora_abstracta():
    with pytest.raises(TypeError):
        RepositorioCreador()


@pytest.mark.parametrize(
    ("creador_cls", "repositorio_cls"),
    [
        (NodoRepositorioCreador, SqlAlchemyNodoRepository),
        (AristaRepositorioCreador, SqlAlchemyAristaRepository),
        (CargaRepositorioCreador, SqlAlchemyCargaRepository),
        (RutaRepositorioCreador, SqlAlchemyRutaRepository),
        (VehiculoDisponibleRepositorioCreador, SqlAlchemyVehiculoDisponibleRepository),
    ],
)
def test_cada_creadora_concreta_fabrica_su_repositorio(creador_cls, repositorio_cls):
    sesion_falsa = object()

    repositorio = creador_cls().obtener_repositorio(sesion_falsa)

    assert isinstance(repositorio, repositorio_cls)


def test_creadoras_usadas_polimorficamente_a_traves_de_la_clase_base():
    """El sello del patron: el codigo que llama a obtener_repositorio() no
    necesita saber cual Creadora concreta esta usando ni que clase de
    repositorio va a recibir."""
    sesion_falsa = object()
    creadoras: list[RepositorioCreador] = [
        NodoRepositorioCreador(),
        AristaRepositorioCreador(),
        CargaRepositorioCreador(),
        RutaRepositorioCreador(),
        VehiculoDisponibleRepositorioCreador(),
    ]

    repositorios = [c.obtener_repositorio(sesion_falsa) for c in creadoras]

    tipos = {type(r).__name__ for r in repositorios}
    assert tipos == {
        "SqlAlchemyNodoRepository",
        "SqlAlchemyAristaRepository",
        "SqlAlchemyCargaRepository",
        "SqlAlchemyRutaRepository",
        "SqlAlchemyVehiculoDisponibleRepository",
    }
