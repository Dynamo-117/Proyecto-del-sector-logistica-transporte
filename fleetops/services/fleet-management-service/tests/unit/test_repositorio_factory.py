import pytest

from app.infrastructure.db.conductor_repository import SqlAlchemyConductorRepository
from app.infrastructure.db.repositorio_factory import (
    RepositorioFactory,
    SqlAlchemyRepositorioFactory,
)
from app.infrastructure.db.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.db.vehiculo_repository import SqlAlchemyVehiculoRepository
from tests.unit.fakes import (
    FakeConductorRepository,
    FakeRepositorioFactory,
    FakeUsuarioRepository,
    FakeVehiculoRepository,
)


def test_no_se_puede_instanciar_la_fabrica_abstracta():
    with pytest.raises(TypeError):
        RepositorioFactory()


def test_fabrica_sqlalchemy_construye_la_familia_de_repositorios_reales():
    factory = SqlAlchemyRepositorioFactory()
    sesion_falsa = object()

    assert isinstance(factory.crear_vehiculo_repo(sesion_falsa), SqlAlchemyVehiculoRepository)
    assert isinstance(factory.crear_conductor_repo(sesion_falsa), SqlAlchemyConductorRepository)
    assert isinstance(factory.crear_usuario_repo(sesion_falsa), SqlAlchemyUsuarioRepository)


def test_fabrica_fake_construye_la_familia_de_repositorios_en_memoria():
    factory = FakeRepositorioFactory()

    assert isinstance(factory.crear_vehiculo_repo(), FakeVehiculoRepository)
    assert isinstance(factory.crear_conductor_repo(), FakeConductorRepository)
    assert isinstance(factory.crear_usuario_repo(), FakeUsuarioRepository)


def _nombres_de_la_familia(factory: RepositorioFactory, sesion: object) -> set[str]:
    """Codigo "cliente": solo conoce RepositorioFactory (la fabrica
    abstracta), nunca una fabrica ni un repositorio concretos. El sello
    del patron: esta misma funcion sirve para cualquier familia."""
    return {
        type(factory.crear_vehiculo_repo(sesion)).__name__,
        type(factory.crear_conductor_repo(sesion)).__name__,
        type(factory.crear_usuario_repo(sesion)).__name__,
    }


def test_intercambiar_la_familia_completa_cambiando_una_sola_fabrica():
    familia_real = _nombres_de_la_familia(SqlAlchemyRepositorioFactory(), sesion=object())
    familia_fake = _nombres_de_la_familia(FakeRepositorioFactory(), sesion=object())

    assert familia_real == {
        "SqlAlchemyVehiculoRepository",
        "SqlAlchemyConductorRepository",
        "SqlAlchemyUsuarioRepository",
    }
    assert familia_fake == {
        "FakeVehiculoRepository",
        "FakeConductorRepository",
        "FakeUsuarioRepository",
    }
    # Ninguna familia mezcla repositorios de la otra.
    assert familia_real.isdisjoint(familia_fake)


def test_fabrica_fake_devuelve_la_misma_instancia_en_llamadas_repetidas():
    """Dentro de una misma 'peticion' (un mismo factory), pedir el mismo
    repositorio dos veces debe devolver el mismo objeto -- para que el
    estado se comparta, igual que compartir una sesion real."""
    factory = FakeRepositorioFactory()

    assert factory.crear_vehiculo_repo() is factory.crear_vehiculo_repo()
