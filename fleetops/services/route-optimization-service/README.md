# route-optimization-service

Microservicio de optimizacion de rutas: calcula la ruta mas corta entre dos puntos de un grafo interno (Dijkstra) y asigna la carga al vehiculo disponible mas adecuado (greedy: menor capacidad suficiente).

## Arquitectura

Hexagonal: `domain` (entidades, excepciones y el algoritmo de Dijkstra, puros) -> `application` (casos de uso + puertos) -> `infrastructure`/`api` (adaptadores concretos). Ver `app/`.

Este servicio mantiene su propio grafo de nodos y conexiones (no usa mapas reales: eso lo hace [`navigation-integration-service`](../navigation-integration-service) via OSRM). Tambien mantiene un modelo de lectura local de que vehiculos existen y su disponibilidad, sincronizado escuchando en RabbitMQ los eventos que publica [`fleet-management-service`](../fleet-management-service) (`vehiculo.creado`, `vehiculo.actualizado`, `vehiculo.conductor_asignado`, `vehiculo.conductor_desasignado`).

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
uvicorn app.main:app --reload --port 8003
```

Documentacion interactiva: http://localhost:8003/docs

## Pruebas

```bash
pytest --cov=app --cov-report=term-missing
```

## Endpoints principales

| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/nodos` | Crear un nodo del grafo (ciudad, bodega, cruce) |
| GET | `/nodos` | Listar nodos |
| POST | `/nodos/{id}/conexiones` | Crear una conexion (arista bidireccional) entre dos nodos |
| POST | `/cargas` | Solicitar asignacion: calcula ruta y asigna vehiculo |
| GET | `/rutas` | Listar rutas activas |
| GET | `/rutas/{id}` | Obtener una ruta |
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness (DB + RabbitMQ) |

## Flujo de ejemplo

```bash
# 1. Crear dos nodos
BOGOTA=$(curl -s -X POST localhost:8003/nodos -H "Content-Type: application/json" \
  -d '{"nombre":"Bogota","latitud":4.71,"longitud":-74.07}' | jq -r .id)
MEDELLIN=$(curl -s -X POST localhost:8003/nodos -H "Content-Type: application/json" \
  -d '{"nombre":"Medellin","latitud":6.25,"longitud":-75.56}' | jq -r .id)

# 2. Conectarlos
curl -X POST localhost:8003/nodos/$BOGOTA/conexiones -H "Content-Type: application/json" \
  -d "{\"nodo_destino_id\":\"$MEDELLIN\",\"distancia_km\":415}"

# 3. Solicitar asignacion (requiere al menos un vehiculo DISPONIBLE ya sincronizado via RabbitMQ)
curl -X POST localhost:8003/cargas -H "Content-Type: application/json" \
  -d "{\"origen_nodo_id\":\"$BOGOTA\",\"destino_nodo_id\":\"$MEDELLIN\",\"peso_kg\":500,\"volumen_m3\":2}"
```

## Eventos consumidos (RabbitMQ)

Cola `route-optimization.vehiculo-eventos` ligada con routing key `vehiculo.*` sobre el exchange `fleetops.events`:

- `vehiculo.creado` / `vehiculo.actualizado` -> registra/actualiza el vehiculo en el modelo de lectura local (placa, capacidad, estado).
- `vehiculo.conductor_asignado` -> marca el vehiculo como `EN_RUTA` localmente.
- `vehiculo.conductor_desasignado` -> marca el vehiculo como `DISPONIBLE` localmente.
