import httpx


async def test_health_devuelve_ok(client):
    respuesta = await client.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


async def test_ready_ok_cuando_todos_los_backends_responden(client):
    respuesta = await client.get("/ready")

    assert respuesta.status_code == 200
    body = respuesta.json()
    assert body["status"] == "ok"
    assert all(body["checks"].values())
    assert set(body["checks"]) == {"fleet", "tracking", "routing", "maintenance", "navigation"}


async def test_ready_degradado_si_un_backend_falla(app, client):
    def handler(request: httpx.Request) -> httpx.Response:
        if ":8003" in str(request.url):
            return httpx.Response(500)
        return httpx.Response(200)

    app.state.http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    respuesta = await client.get("/ready")

    assert respuesta.status_code == 503
    body = respuesta.json()
    assert body["status"] == "degraded"
    assert body["checks"]["routing"] is False
    assert body["checks"]["fleet"] is True
