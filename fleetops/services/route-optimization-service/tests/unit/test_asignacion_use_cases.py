from uuid import uuid4

import pytest

from app.application.use_cases.asignacion_use_cases import (
    ListarRutasActivas,
    ObtenerRuta,
    SolicitarAsignacionCarga,
)
from app.domain.entities import Arista, EstadoVehiculo, Nodo, VehiculoDisponible
from app.domain.exceptions import (
    NodoNoEncontrado,
    RutaNoEncontrada,
    SinRutaEnGrafo,
    SinVehiculoDisponible,
)
from tests.unit.fakes import (
    FakeAristaRepository,
    FakeCargaRepository,
    FakeNodoRepository,
    FakeRutaRepository,
    FakeVehiculoDisponibleRepository,
)


@pytest.fixture
def repos():
    return {
        "nodo": FakeNodoRepository(),
        "arista": FakeAristaRepository(),
        "carga": FakeCargaRepository(),
        "ruta": FakeRutaRepository(),
        "vehiculo": FakeVehiculoDisponibleRepository(),
    }


async def _crear_conexion(repos, distancia_km: float = 10) -> tuple:
    origen = Nodo(nombre="Bogota", latitud=4.71, longitud=-74.07)
    destino = Nodo(nombre="Medellin", latitud=6.25, longitud=-75.56)
    await repos["nodo"].crear(origen)
    await repos["nodo"].crear(destino)
    await repos["arista"].crear(
        Arista(nodo_origen_id=origen.id, nodo_destino_id=destino.id, distancia_km=distancia_km)
    )
    return origen, destino


def _use_case(repos) -> SolicitarAsignacionCarga:
    return SolicitarAsignacionCarga(
        repos["nodo"], repos["arista"], repos["carga"], repos["ruta"], repos["vehiculo"]
    )


async def test_solicitar_asignacion_con_nodo_origen_desconocido_falla(repos):
    _, destino = await _crear_conexion(repos)

    with pytest.raises(NodoNoEncontrado):
        await _use_case(repos).ejecutar(uuid4(), destino.id, 100, 1)


async def test_solicitar_asignacion_sin_camino_en_el_grafo_falla(repos):
    origen = Nodo(nombre="A", latitud=0, longitud=0)
    destino = Nodo(nombre="B", latitud=1, longitud=1)
    await repos["nodo"].crear(origen)
    await repos["nodo"].crear(destino)

    with pytest.raises(SinRutaEnGrafo):
        await _use_case(repos).ejecutar(origen.id, destino.id, 100, 1)


async def test_solicitar_asignacion_sin_vehiculo_disponible_falla(repos):
    origen, destino = await _crear_conexion(repos)

    with pytest.raises(SinVehiculoDisponible):
        await _use_case(repos).ejecutar(origen.id, destino.id, 500, 1)


async def test_solicitar_asignacion_elige_vehiculo_de_menor_capacidad_suficiente(repos):
    origen, destino = await _crear_conexion(repos, distancia_km=25)
    grande = VehiculoDisponible(
        id=uuid4(), placa="GRANDE", capacidad_kg=2000, estado=EstadoVehiculo.DISPONIBLE
    )
    justo = VehiculoDisponible(
        id=uuid4(), placa="JUSTO", capacidad_kg=600, estado=EstadoVehiculo.DISPONIBLE
    )
    await repos["vehiculo"].registrar_o_actualizar(grande)
    await repos["vehiculo"].registrar_o_actualizar(justo)

    ruta = await _use_case(repos).ejecutar(origen.id, destino.id, 500, 1)

    assert ruta.vehiculo_id == justo.id
    assert ruta.distancia_km == 25
    assert ruta.nodos == [origen.id, destino.id]

    carga = await repos["carga"].obtener(ruta.carga_id)
    assert carga.estado.value == "ASIGNADA"


async def test_solicitar_asignacion_no_reutiliza_vehiculo_con_ruta_activa(repos):
    origen, destino = await _crear_conexion(repos)
    unico = VehiculoDisponible(
        id=uuid4(), placa="UNICO", capacidad_kg=1000, estado=EstadoVehiculo.DISPONIBLE
    )
    await repos["vehiculo"].registrar_o_actualizar(unico)

    use_case = _use_case(repos)
    await use_case.ejecutar(origen.id, destino.id, 100, 1)

    with pytest.raises(SinVehiculoDisponible):
        await use_case.ejecutar(origen.id, destino.id, 100, 1)


async def test_obtener_ruta_inexistente_falla(repos):
    with pytest.raises(RutaNoEncontrada):
        await ObtenerRuta(repos["ruta"]).ejecutar(uuid4())


async def test_listar_rutas_activas(repos):
    origen, destino = await _crear_conexion(repos)
    vehiculo = VehiculoDisponible(
        id=uuid4(), placa="ABC", capacidad_kg=1000, estado=EstadoVehiculo.DISPONIBLE
    )
    await repos["vehiculo"].registrar_o_actualizar(vehiculo)
    await _use_case(repos).ejecutar(origen.id, destino.id, 100, 1)

    rutas = await ListarRutasActivas(repos["ruta"]).ejecutar()

    assert len(rutas) == 1
