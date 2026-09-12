# FleetOps

Sistema de gestion de flotas para logistica y transporte, compuesto por microservicios independientes (arquitectura hexagonal por servicio).

> **Fase actual: Fase 2 — implementacion funcional nucleo.** No se aplican ni se nombran patrones de diseno GoF todavia; eso corresponde a la Fase 3.

## Microservicios

Los seis microservicios de la Fase 2 estan implementados: CRUD/reglas de negocio, pruebas (unitarias + integracion, ≥80% cobertura), manejo de errores uniforme, logging estructurado con `correlation_id`, `/health`/`/ready` y configuracion por entorno.

| Servicio | Puerto | Descripcion |
|---|---|---|
| [`fleet-management-service`](services/fleet-management-service) | 8000 | CRUD de vehiculos y conductores, asignacion conductor-vehiculo |
| [`vehicle-tracking-service`](services/vehicle-tracking-service) | 8002 | Ingestion de telemetria, estado en tiempo real (SSE) |
| [`route-optimization-service`](services/route-optimization-service) | 8003 | Grafo interno + Dijkstra, asignacion de cargas a vehiculos |
| [`predictive-maintenance-service`](services/predictive-maintenance-service) | 8004 | Alertas de mantenimiento por umbrales de km/horas de motor |
| [`navigation-integration-service`](services/navigation-integration-service) | 8005 | Integracion normalizada con OSRM/OpenStreetMap |
| [`api-gateway`](services/api-gateway) | 8080 | Punto de entrada unico (proxy inverso FastAPI + httpx) |

Los servicios se comunican entre si de forma asincrona via RabbitMQ (exchange topic `fleetops.events`): `fleet-management-service` publica eventos de vehiculos (`vehiculo.creado`, `vehiculo.actualizado`, `vehiculo.conductor_asignado`, `vehiculo.conductor_desasignado`) que `vehicle-tracking-service`, `route-optimization-service` y `predictive-maintenance-service` consumen para mantener su propio modelo de lectura de vehiculos. `navigation-integration-service` y `api-gateway` no usan RabbitMQ.

## Levantar el entorno local

Cada microservicio corre de forma independiente con un entorno virtual de Python (sin Docker). Ver las instrucciones especificas en el README de cada servicio, por ejemplo [`fleet-management-service`](services/fleet-management-service).

Resumen general:

```bash
cd services/fleet-management-service
python -m venv .venv
.venv\Scripts\activate      # en Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing
```

Las pruebas de cada servicio usan una base de datos SQLite en memoria y dobles de prueba para mensajeria (o mocks de red, en `navigation-integration-service` y `api-gateway`), por lo que ninguna requiere PostgreSQL, RabbitMQ ni red real. Para correr un servicio de forma real (`uvicorn app.main:app`) si hace falta tener Postgres y RabbitMQ instalados localmente y apuntar `DATABASE_URL`/`RABBITMQ_URL` en su `.env` a esas instancias (`navigation-integration-service` y `api-gateway` no necesitan Postgres/RabbitMQ).

### Levantar el sistema completo end-to-end

Con Postgres y RabbitMQ corriendo localmente (uno por servicio o compartidos, segun prefieras), y cada servicio con su `.env`, `pip install` y `alembic upgrade head` (donde aplique) ya hechos, en seis terminales distintas:

```bash
# 1-5: cualquier orden entre ellos, pero antes que el gateway
uvicorn app.main:app --port 8000   # en services/fleet-management-service
uvicorn app.main:app --port 8002   # en services/vehicle-tracking-service
uvicorn app.main:app --port 8003   # en services/route-optimization-service
uvicorn app.main:app --port 8004   # en services/predictive-maintenance-service
uvicorn app.main:app --port 8005   # en services/navigation-integration-service

# 6: al final, para que /ready pueda ver los demas arriba
uvicorn app.main:app --port 8080   # en services/api-gateway
```

Luego todo el trafico de cliente puede ir a `http://localhost:8080` (ver el mapa de rutas en el README de `api-gateway`).

## Estructura del repositorio

```
fleetops/
├── services/
│   ├── fleet-management-service/
│   ├── vehicle-tracking-service/
│   ├── route-optimization-service/
│   ├── predictive-maintenance-service/
│   ├── navigation-integration-service/
│   └── api-gateway/
├── docs/
│   ├── adr/
│   └── uml/
└── .github/workflows/
```

## Convenciones

- Commits: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`).
- Una rama por servicio o por feature (`feature/fleet-management-crud`), merge a `main` via PR.
- Formateo con Black, linting con Ruff.
