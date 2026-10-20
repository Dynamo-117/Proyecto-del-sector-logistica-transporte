import httpx


def _backend(caidos: tuple[str, ...] = ()):
    """Simula los 4 microservicios detras del gateway, segun el puerto de la URL."""

    def handler(request: httpx.Request) -> httpx.Response:
        ruta, puerto = request.url.path, request.url.port
        if puerto in {int(c) for c in caidos}:
            raise httpx.ConnectError("caido", request=request)
        if puerto == 8000 and ruta == "/vehiculos":
            return httpx.Response(
                200, json=[{"id": "v1", "estado": "DISPONIBLE"}, {"id": "v2", "estado": "EN_RUTA"}]
            )
        if puerto == 8000 and ruta == "/conductores":
            return httpx.Response(200, json=[{"estado": "DISPONIBLE"}])
        if puerto == 8003 and ruta == "/rutas":
            return httpx.Response(200, json=[{"distancia_km": 415.0}])
        if puerto == 8004:
            return httpx.Response(200, json=[{}] if "v1" in ruta else [])
        if puerto == 8002:
            return httpx.Response(200, json={"estado_movimiento": "EN_MOVIMIENTO"})
        return httpx.Response(404)

    return handler


async def test_resumen_arma_la_respuesta_con_una_sola_llamada(app, client):
    app.state.http_client = httpx.AsyncClient(transport=httpx.MockTransport(_backend()))

    respuesta = await client.get("/resumen")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["flota"]["total_vehiculos"] == 2
    assert cuerpo["flota"]["vehiculos_por_estado"] == {"DISPONIBLE": 1, "EN_RUTA": 1}
    assert cuerpo["rutas"] == {"disponible": True, "rutas_activas": 1, "distancia_total_km": 415.0}
    assert cuerpo["mantenimiento"]["alertas_activas"] == 1
    assert cuerpo["tracking"]["en_movimiento"] == 2
    assert cuerpo["llamadas_internas"] == 3 + 2 * 2


async def test_resumen_con_un_servicio_caido_marca_esa_seccion(app, client):
    app.state.http_client = httpx.AsyncClient(transport=httpx.MockTransport(_backend(("8003",))))

    cuerpo = (await client.get("/resumen")).json()

    assert cuerpo["rutas"]["disponible"] is False
    assert cuerpo["flota"]["disponible"] is True


async def test_resumen_exige_autenticacion(client_sin_auth):
    respuesta = await client_sin_auth.get("/resumen")

    assert respuesta.status_code == 401
