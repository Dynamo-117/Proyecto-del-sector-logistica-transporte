# fleet-management-service

Microservicio de gestion de flota: CRUD de vehiculos y conductores, asignacion conductor-vehiculo, y autenticacion (login + emision de JWT) para toda la plataforma FleetOps. Publica eventos de dominio a RabbitMQ.

## Arquitectura

Hexagonal: `domain` (entidades/excepciones puras) -> `application` (casos de uso + puertos) -> `infrastructure`/`api` (adaptadores concretos). Ver `app/`.

## Requisitos

- Python 3.12 (probado tambien con 3.13)
- PostgreSQL 16 instalado localmente, para correr el servicio contra una base real
- RabbitMQ instalado localmente, para publicar/consumir eventos reales

No se usa Docker en este proyecto: todo corre con un entorno virtual de Python. Las pruebas (ver mas abajo) no requieren tener Postgres ni RabbitMQ instalados.

## Configuracion

Copia `.env.example` a `.env` y ajusta los valores.

```bash
cp .env.example .env
```

## Instalacion local

```bash
python -m venv .venv
source .venv/bin/activate  # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Migraciones

```bash
alembic upgrade head
```

Para crear una nueva migracion tras cambiar los modelos en `app/infrastructure/db/models.py`:

```bash
alembic revision --autogenerate -m "descripcion del cambio"
```

## Ejecutar el servicio

```bash
uvicorn app.main:app --reload --port 8000
```

Documentacion interactiva (Swagger): http://localhost:8000/docs

## Crear el primer usuario ADMINISTRADOR

Tras correr las migraciones, no existe ningun usuario todavia. Crea el primero con el script de seed (pide la contrasena de forma interactiva, no la hardcodees):

```bash
python -m scripts.crear_usuario_admin --email admin@fleetops.com
```

## Pruebas

```bash
pytest --cov=app --cov-report=term-missing
```

Las pruebas de integracion usan SQLite en memoria y un publicador de eventos falso, por lo que **no** requieren PostgreSQL ni RabbitMQ corriendo. Las migraciones con Alembic (Postgres) son solo para el entorno real/demo.

## Endpoints principales

| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/auth/login` | Iniciar sesion (email + password) y obtener un JWT |
| GET | `/auth/me` | Usuario actual a partir del JWT (header `Authorization: Bearer <token>`) |
| POST | `/vehiculos` | Crear vehiculo |
| GET | `/vehiculos` | Listar vehiculos |
| GET | `/vehiculos/{id}` | Obtener vehiculo |
| PATCH | `/vehiculos/{id}` | Actualizar vehiculo |
| DELETE | `/vehiculos/{id}` | Eliminar vehiculo |
| POST | `/vehiculos/{id}/asignar-conductor` | Asignar conductor a vehiculo |
| POST | `/vehiculos/{id}/desasignar-conductor` | Liberar conductor de vehiculo |
| POST | `/conductores` | Crear conductor |
| GET | `/conductores` | Listar conductores |
| GET | `/conductores/{id}` | Obtener conductor |
| PATCH | `/conductores/{id}` | Actualizar conductor |
| DELETE | `/conductores/{id}` | Eliminar conductor |
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness (DB + RabbitMQ) |

## Eventos publicados (RabbitMQ, exchange topic `fleetops.events`)

- `vehiculo.creado`
- `vehiculo.actualizado`
- `vehiculo.conductor_asignado`
- `vehiculo.conductor_desasignado`
