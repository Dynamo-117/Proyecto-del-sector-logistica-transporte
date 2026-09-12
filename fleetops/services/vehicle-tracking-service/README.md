# vehicle-tracking-service

Microservicio de monitoreo en tiempo real: ingesta telemetria (posicion GPS, velocidad) de los vehiculos de la flota, guarda su historico y expone el estado actual y un stream en vivo (SSE) por vehiculo.

## Arquitectura

Hexagonal: `domain` (entidades/excepciones puras) -> `application` (casos de uso + puertos) -> `infrastructure`/`api` (adaptadores concretos). Ver `app/`.

Este servicio no conoce por si mismo que vehiculos existen: se entera escuchando el evento `vehiculo.creado` que publica [`fleet-management-service`](../fleet-management-service) en RabbitMQ (exchange topic `fleetops.events`). Ingestar telemetria de un vehiculo que este servicio no ha "visto" todavia devuelve `404 VEHICULO_DESCONOCIDO`.

## Requisitos

- Python 3.12 (probado tambien con 3.13)
- PostgreSQL 16 con la extension **TimescaleDB** instalada localmente, para correr contra una base real (la tabla `telemetria` se convierte en hypertable via Alembic)
- RabbitMQ instalado localmente, para recibir eventos de `fleet-management-service`

No se usa Docker en este proyecto. Las pruebas no requieren Postgres/TimescaleDB ni RabbitMQ: usan SQLite en memoria y dobles de prueba.

## Configuracion

```bash
cp .env.example .env
```

## Instalacion local

```bash
python -m venv .venv
.venv\Scripts\activate      # en Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

## Migraciones

```bash
alembic upgrade head
```

La migracion inicial crea `CREATE EXTENSION IF NOT EXISTS timescaledb` y convierte `telemetria` en hypertable — requiere que la extension este disponible en el Postgres destino.

## Ejecutar el servicio

```bash
uvicorn app.main:app --reload --port 8002
```

Documentacion interactiva: http://localhost:8002/docs

## Pruebas

```bash
pytest --cov=app --cov-report=term-missing
```

El stream SSE (`/vehiculos/{id}/eventos`) no se puede probar de punta a punta con `httpx` + `ASGITransport`: ese transporte de pruebas buferiza toda la respuesta antes de devolverla, lo cual es incompatible con una respuesta infinita como un SSE. Por eso su logica (generador + broadcaster) se prueba invocando la funcion de la ruta directamente en `tests/unit/test_stream_routes.py`; en un servidor real (uvicorn) el streaming funciona de forma normal.

## Endpoints principales

| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/telemetria` | Ingestar un punto de telemetria |
| GET | `/vehiculos/{id}/estado` | Ultima lectura conocida (posicion, velocidad, en movimiento/detenido) |
| GET | `/vehiculos/{id}/historico` | Historico de telemetria (filtros `desde`/`hasta`, paginacion) |
| GET | `/vehiculos/{id}/eventos` | Stream SSE en tiempo real de nuevas lecturas |
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness (DB + RabbitMQ) |

## Simulador de telemetria

Como no hay dispositivos GPS reales, `scripts/simulador_telemetria.py` envia lecturas aleatorias a intervalos regulares para un vehiculo ya conocido por el servicio:

```bash
python scripts/simulador_telemetria.py <vehiculo_id> --url http://localhost:8002 --intervalo 2
```

El `<vehiculo_id>` debe ser el `id` de un vehiculo creado en `fleet-management-service` (y ya propagado a este servicio via RabbitMQ).

## Eventos consumidos (RabbitMQ)

- `vehiculo.creado` (de `fleet-management-service`, exchange `fleetops.events`) -> registra el vehiculo como "conocido" para poder ingestar su telemetria.
