# Servicios de FleetOps: qué hace cada uno, qué usa el frontend hoy, y cómo los afecta el Singleton

Este documento responde tres preguntas concretas:

1. ¿Qué hace cada uno de los 6 microservicios?
2. ¿Cuáles de esos servicios están realmente conectados al frontend hoy?
3. ¿Cómo afecta el patrón Singleton (aplicado en `docs/patrones/singleton.md`) al funcionamiento de cada servicio?

## 1. Qué hace cada servicio

| # | Servicio | Puerto | Rol |
|---|---|---|---|
| 1 | `fleet-management-service` | 8000 | Fuente de verdad de vehículos/conductores + autenticación |
| 2 | `vehicle-tracking-service` | 8002 | Telemetría GPS en tiempo real |
| 3 | `route-optimization-service` | 8003 | Cálculo de rutas y asignación de cargas |
| 4 | `predictive-maintenance-service` | 8004 | Alertas de mantenimiento por desgaste |
| 5 | `navigation-integration-service` | 8005 | Proxy normalizado hacia OSRM (mapas externos) |
| 6 | `api-gateway` | 8080 | Punto de entrada único + autenticación JWT |

### 1.1 `fleet-management-service` (8000)

Es la **fuente de verdad** de vehículos y conductores de toda la plataforma, y desde la Fase 3 también el dueño de la autenticación.

- CRUD de vehículos y conductores, y la operación de asignar/desasignar conductor a vehículo.
- Login (`POST /auth/login`) y usuario actual (`GET /auth/me`): entidad `Usuario`, contraseñas con bcrypt, JWT firmado.
- Cada vez que crea, actualiza o (des)asigna un vehículo, **publica un evento** al exchange `fleetops.events` de RabbitMQ (`vehiculo.creado`, `vehiculo.actualizado`, `vehiculo.conductor_asignado`, `vehiculo.conductor_desasignado`). Ningún otro servicio le pregunta directamente por HTTP — todos los demás se enteran por estos eventos.
- Tiene su propia base de datos PostgreSQL (`fleet_management`).

### 1.2 `vehicle-tracking-service` (8002)

Monitoreo en tiempo real: ingesta posición GPS y velocidad, guarda el histórico y expone el estado actual más un stream en vivo por vehículo (Server-Sent Events).

- No sabe qué vehículos existen por sí mismo: escucha `vehiculo.creado` en RabbitMQ para "conocer" un vehículo antes de poder recibir su telemetría (si no lo conoce, responde `404 VEHICULO_DESCONOCIDO`).
- Usa **TimescaleDB** (extensión de Postgres) para la tabla de telemetría, porque es una serie de tiempo.
- Incluye un script simulador (`scripts/simulador_telemetria.py`) porque no hay dispositivos GPS reales.

### 1.3 `route-optimization-service` (8003)

Calcula la ruta más corta entre dos puntos de un **grafo propio** (algoritmo de Dijkstra, sin mapas reales) y asigna la carga al vehículo disponible más adecuado (estrategia *greedy*: el de menor capacidad que igual alcance).

- Mantiene su propio modelo de lectura de qué vehículos existen y su disponibilidad, sincronizado escuchando `vehiculo.*` en RabbitMQ.
- Tiene su propia base de datos (nodos, aristas, cargas, rutas, vehículos disponibles).

### 1.4 `predictive-maintenance-service` (8004)

Recibe lecturas de kilometraje/horas de motor (vía REST, simulando el odómetro/ECU del vehículo — **no** viene de `vehicle-tracking-service`, que solo maneja posición GPS) y genera alertas cuando se cruzan umbrales fijos:

| Alerta | Cada | O cada |
|---|---|---|
| `CAMBIO_ACEITE` | 10.000 km | 300 horas de motor |
| `REVISION_GENERAL` | 20.000 km | 600 horas de motor |

- También sincroniza su propio catálogo de vehículos escuchando `vehiculo.creado`/`vehiculo.actualizado` en RabbitMQ.

### 1.5 `navigation-integration-service` (8005)

El más simple de los seis: **sin base de datos, sin RabbitMQ**. Es un proxy normalizador hacia [OSRM](http://project-osrm.org/) (servidor público de rutas sobre OpenStreetMap, gratuito, sin API key). Recibe origen/destino y devuelve distancia, duración y la geometría de la ruta en un formato propio, desacoplado del formato nativo de OSRM.

### 1.6 `api-gateway` (8080)

El único punto de entrada que debería usar un cliente externo (como el frontend). Es un proxy inverso (FastAPI + `httpx`) sin base de datos ni estado propio:

- Reenvía cada petición al microservicio correspondiente según el prefijo de la ruta (`/fleet/*` → 8000, `/tracking/*` → 8002, `/routing/*` → 8003, `/maintenance/*` → 8004, `/navigation/*` → 8005), soporta streaming real (necesario para el SSE de `vehicle-tracking-service`).
- Desde la Fase 3, también valida el JWT de cada petición (excepto `/health`, `/ready` y `POST /fleet/auth/login`) y exige rol `ADMINISTRADOR` para editar/eliminar vehículos o conductores.

### Cómo se comunican entre sí

```
                          ┌────────────────────────┐
   Frontend  ───────────► │      api-gateway        │
   (React)                │  (proxy + JWT, :8080)   │
                          └───────────┬─────────────┘
                                      │ REST
                                      ▼
                          ┌────────────────────────┐
                          │ fleet-management-service │──┐
                          │  (fuente de verdad, :8000)│  │ publica eventos
                          └────────────────────────┘  │ (RabbitMQ, exchange
                                                       │  fleetops.events)
                       ┌───────────────┬───────────────┼─────────────────┐
                       ▼               ▼               ▼                 
              vehicle-tracking  route-optimization  predictive-maintenance
                  (:8002)           (:8003)              (:8004)
```

`navigation-integration-service` (:8005) no habla con nadie del sistema, solo con OSRM (externo). Ningún microservicio de negocio se llama a sí mismo por HTTP directamente — toda la sincronización entre ellos es asíncrona vía eventos.

## 2. ¿Cuáles están conectados al frontend hoy?

**Solo uno: `fleet-management-service`, a través de `api-gateway`.** Los otros cuatro (tracking, routing, maintenance, navigation) están completos, probados y ya serían alcanzables a través del gateway (sus prefijos `/tracking`, `/routing`, `/maintenance`, `/navigation` están registrados en `api-gateway`), pero **ninguna pantalla del frontend los llama todavía**. Existen y funcionan de forma independiente, pero no están "enchufados" a ninguna interfaz visual.

Confirmé esto revisando el código del frontend (`frontend/src/api/*.ts`): las únicas rutas que llama son estas tres, todas bajo el prefijo `/fleet`:

| Archivo del frontend | Endpoint que llama | Servicio real detrás del gateway |
|---|---|---|
| `api/auth.ts` | `POST /fleet/auth/login` | fleet-management-service |
| `api/auth.ts` | `GET /fleet/auth/me` | fleet-management-service |
| `api/vehiculos.ts` | `GET/POST /fleet/vehiculos`, `DELETE /fleet/vehiculos/{id}`, `POST /fleet/vehiculos/{id}/asignar-conductor`, `.../desasignar-conductor` | fleet-management-service |
| `api/conductores.ts` | `GET/POST /fleet/conductores`, `DELETE /fleet/conductores/{id}` | fleet-management-service |

El flujo real es: **Frontend (`localhost:5173`) → `api-gateway` (`localhost:8080`, valida el JWT) → `fleet-management-service` (`localhost:8000`)**. El gateway reenvía la petición quitando el prefijo `/fleet` (`GET /fleet/vehiculos` se convierte en `GET http://localhost:8000/vehiculos`).

Si más adelante quieres mostrar en el frontend el mapa en vivo (`vehicle-tracking-service`), rutas optimizadas (`route-optimization-service`), alertas de mantenimiento (`predictive-maintenance-service`) o cálculo de rutas (`navigation-integration-service`), el backend ya está listo — solo faltaría agregar las páginas/llamadas correspondientes en `frontend/src/api/` y `frontend/src/pages/`, usando los prefijos que ya existen en el gateway.

## 3. Cómo afecta el Singleton a cada servicio

### El mecanismo (recordatorio breve)

Cada servicio tiene su propia clase `Settings` (una por servicio, no compartida entre ellos) que lee su `.env` y expone los valores de configuración: URL de base de datos, URL de RabbitMQ, clave JWT, etc. Antes del patrón, cada servicio confiaba en `@lru_cache` para no releer `.env` en cada llamada a `get_settings()`. Ahora esa garantía es explícita: la propia clase `Settings` controla su única instancia (`_instancia`) y la entrega a través de `obtener_instancia()`. El detalle completo está en [`docs/patrones/singleton.md`](patrones/singleton.md).

**Punto clave:** el Singleton **no cambia qué hace cada servicio** (su lógica de negocio es exactamente la misma antes y después). Lo que cambia es **cómo cada servicio obtiene su propia configuración internamente** — y por eso el efecto es distinto en cada uno, según qué necesita leer de esa configuración.

### Efecto concreto, servicio por servicio

**`fleet-management-service`** — es el que más superficie tiene:
- `main.py`: usa `settings.rabbitmq_url`/`rabbitmq_exchange` para conectar el publicador de eventos, `settings.log_level`/`app_name` para logging, `settings.cors_origins` para CORS.
- `infrastructure/db/session.py`: el motor de SQLAlchemy (`create_async_engine(settings.database_url, ...)`) se crea **una sola vez al importar el módulo**, leyendo del Singleton.
- `api/dependencies.py`: `get_token_service()` llama a `get_settings()` **en cada petición HTTP** que necesita emitir o validar un JWT (login, `/auth/me`). Gracias al Singleton, esa llamada no vuelve a leer `.env` ni revalida nada — solo devuelve la misma instancia ya creada. Este es el caso donde más se nota el patrón: sin él, cada login/petición autenticada podría estar recreando la configuración innecesariamente.
- `scripts/crear_usuario_admin.py`: usa `settings.database_url` para conectarse a la DB al sembrar el primer usuario ADMINISTRADOR.

**`api-gateway`** — usa la configuración para saber *a dónde reenviar*:
- `main.py`: `settings.rutas_servicios` (el diccionario prefijo→URL de cada microservicio) para construir el `ReenviarPeticion`; `settings.jwt_secret_key`/`jwt_algorithm` para instanciar el `JWTAuthMiddleware`; `settings.proxy_timeout_segundos` para el cliente `httpx`.
- `api/routes/health_routes.py`: el endpoint `/ready` recorre `settings.rutas_servicios` para hacer `GET /health` a cada uno de los 5 microservicios registrados.
- Aquí el Singleton importa especialmente porque `settings.jwt_secret_key` **debe ser idéntico** al de `fleet-management-service` (quien firma los tokens) — tener una única instancia estable por proceso evita cualquier inconsistencia entre el momento en que arranca el middleware y el momento en que valida cada petición.

**`vehicle-tracking-service`, `route-optimization-service`, `predictive-maintenance-service`** — los tres siguen el mismo patrón entre sí:
- `infrastructure/db/session.py`: motor de base de datos creado una vez con `settings.database_url`.
- `main.py`: consumidor de RabbitMQ (`RabbitMQConsumer`) creado con `settings.rabbitmq_url`, `rabbitmq_exchange`, `rabbitmq_queue` y `rabbitmq_routing_key` — estos tres últimos son distintos en cada servicio (cada uno escucha una cola y un routing key diferente), pero los lee del mismo tipo de Singleton.
- `alembic/env.py`: las migraciones también leen `settings.database_url` para saber contra qué base de datos aplicar los cambios.

**`navigation-integration-service`** — el más simple, y el que menos depende de la config en tiempo de ejecución:
- `main.py`: solo usa `settings.osrm_base_url` y `settings.osrm_timeout_segundos` para construir el `OSRMClient` al arrancar, más `log_level`/`app_name`/`cors_origins`. No hay DB ni RabbitMQ que configurar, así que no hay `session.py` ni `alembic/env.py` leyendo el Singleton.

### En resumen

| Servicio | Qué lee de su Settings singleton |
|---|---|
| fleet-management-service | DB, RabbitMQ, JWT (por petición), logging, CORS |
| api-gateway | Rutas de los 5 microservicios, JWT, timeout del proxy, logging, CORS |
| vehicle-tracking-service | DB (+ Alembic), RabbitMQ (cola/routing key propios), logging, CORS |
| route-optimization-service | DB (+ Alembic), RabbitMQ (cola/routing key propios), logging, CORS |
| predictive-maintenance-service | DB (+ Alembic), RabbitMQ (cola/routing key propios), logging, CORS |
| navigation-integration-service | URL/timeout de OSRM, logging, CORS |

En los seis casos el efecto de fondo es el mismo: cada proceso lee su `.env` **una sola vez**, de forma explícita y con nombre (`obtener_instancia()`), en vez de depender implícitamente de que nadie quite un decorador. El comportamiento observable de cada servicio (endpoints, respuestas, eventos) es idéntico a como era antes de aplicar el patrón — por eso los 169 tests de los 6 servicios siguen pasando sin ningún cambio.
