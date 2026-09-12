# predictive-maintenance-service

Microservicio de mantenimiento predictivo: recibe lecturas de kilometraje y horas de motor, aplica umbrales fijos de desgaste y genera alertas de mantenimiento activas por vehiculo.

## Arquitectura

Hexagonal: `domain` (entidades, excepciones y la evaluacion de umbrales, puros) -> `application` (casos de uso + puertos) -> `infrastructure`/`api` (adaptadores concretos). Ver `app/`.

Al igual que `route-optimization-service`, este servicio mantiene su propio modelo de lectura de que vehiculos existen, sincronizado escuchando en RabbitMQ los eventos `vehiculo.creado`/`vehiculo.actualizado` de [`fleet-management-service`](../fleet-management-service). Las lecturas de kilometraje/horas de motor **no** vienen de `vehicle-tracking-service` (que solo maneja posicion/velocidad GPS): se ingieren directamente via REST, simulando la telemetria propia del vehiculo (odometro, ECU).

## Umbrales de mantenimiento (fijos, Fase 2)

| Tipo de alerta | Cada | O cada |
|---|---|---|
| `CAMBIO_ACEITE` | 10.000 km | 300 horas de motor |
| `REVISION_GENERAL` | 20.000 km | 600 horas de motor |

El contador de desgaste de cada tipo se reinicia a la lectura mas reciente del vehiculo cuando su alerta se marca como completada (`POST /alertas/{id}/completar`), no al momento de crearse.

## Requisitos

- Python 3.12 (probado tambien con 3.13)
- PostgreSQL 16 instalado localmente, para correr contra una base real
- RabbitMQ instalado localmente, para recibir eventos de `fleet-management-service`

No se usa Docker. Las pruebas no requieren Postgres ni RabbitMQ: usan SQLite en memoria y dobles de prueba.

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

## Ejecutar el servicio

```bash
uvicorn app.main:app --reload --port 8004
```

Documentacion interactiva: http://localhost:8004/docs

## Pruebas

```bash
pytest --cov=app --cov-report=term-missing
```

## Endpoints principales

| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/lecturas` | Registrar una lectura de kilometraje/horas de motor |
| GET | `/vehiculos/{id}/alertas` | Listar alertas activas de un vehiculo |
| POST | `/alertas/{id}/completar` | Marcar una alerta como mantenimiento realizado |
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness (DB + RabbitMQ) |

## Eventos consumidos (RabbitMQ)

Cola `predictive-maintenance.vehiculo-eventos` ligada con routing key `vehiculo.*` sobre el exchange `fleetops.events`; solo se procesan `vehiculo.creado` y `vehiculo.actualizado` (se ignoran los eventos de asignacion de conductor, irrelevantes para este servicio).
