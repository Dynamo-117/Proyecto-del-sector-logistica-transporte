# navigation-integration-service

Microservicio de integracion con navegacion: expone un endpoint propio y normalizado de "calcular ruta entre dos puntos", que internamente llama al proveedor externo [OSRM](http://project-osrm.org/) (Open Source Routing Machine) sobre datos de OpenStreetMap. OSRM es gratuito y no requiere API key.

## Arquitectura

Hexagonal: `domain` (entidades/excepciones puras) -> `application` (caso de uso + puerto `NavigationProvider`) -> `infrastructure/external` (adaptador `OSRMClient`) / `api` (adaptador HTTP entrante). Ver `app/`.

Es el mas simple de los microservicios de FleetOps: no tiene base de datos ni se conecta a RabbitMQ, es un proxy normalizador sin estado hacia el servidor publico de OSRM.

## Requisitos

- Python 3.12 (probado tambien con 3.13)
- Acceso a internet saliente hacia `router.project-osrm.org` (o tu propia instancia de OSRM, configurable via `OSRM_BASE_URL`)

No se usa Docker.

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

## Ejecutar el servicio

```bash
uvicorn app.main:app --reload --port 8005
```

Documentacion interactiva: http://localhost:8005/docs

## Pruebas

```bash
pytest --cov=app --cov-report=term-missing
```

Ninguna prueba llama a la red real: el cliente OSRM se prueba con `httpx.MockTransport` (respuestas simuladas), y las pruebas de integracion de la API sobreescriben el proveedor de navegacion por uno falso.

## Endpoints principales

| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/rutas/calcular` | Calcular ruta entre un origen y un destino (lat/lon) |
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness (siempre `ok`: no hay DB/broker propios; el proveedor externo se consulta bajo demanda, no en cada readiness check, para no saturar el servidor publico) |

## Ejemplo

```bash
curl -X POST localhost:8005/rutas/calcular -H "Content-Type: application/json" -d '{
  "origen": {"latitud": 4.71, "longitud": -74.07},
  "destino": {"latitud": 6.25, "longitud": -75.56}
}'
```

Respuesta normalizada (independiente del formato propio de OSRM):

```json
{
  "origen": {"latitud": 4.71, "longitud": -74.07},
  "destino": {"latitud": 6.25, "longitud": -75.56},
  "distancia_km": 415.2,
  "duracion_min": 331.4,
  "puntos": [{"latitud": 4.71, "longitud": -74.07}, "..."]
}
```
