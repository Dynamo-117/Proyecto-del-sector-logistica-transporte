# api-gateway

Punto de entrada unico de FleetOps: un proxy inverso (FastAPI + `httpx`) que enruta cada peticion al microservicio correspondiente segun el prefijo de la ruta, con soporte de streaming real (incluye el SSE de `vehicle-tracking-service`).

## Arquitectura

Hexagonal: `domain` (excepciones) -> `application` (caso de uso `ReenviarPeticion` + puerto `ProxyClient`) -> `infrastructure/external` (`HttpxProxyClient`) / `api` (ruta catch-all). Ver `app/`.

No tiene base de datos ni se conecta a RabbitMQ: es un enrutador sin estado. No se usa Traefik ni Docker; es la variante "FastAPI + httpx" que plantea el enunciado como alternativa mas simple.

## Mapa de rutas

| Prefijo | Servicio destino | Puerto por defecto |
|---|---|---|
| `/fleet/*` | fleet-management-service | 8000 |
| `/tracking/*` | vehicle-tracking-service | 8002 |
| `/routing/*` | route-optimization-service | 8003 |
| `/maintenance/*` | predictive-maintenance-service | 8004 |
| `/navigation/*` | navigation-integration-service | 8005 |

El prefijo se quita antes de reenviar: `GET /fleet/vehiculos/123` se convierte en `GET http://localhost:8000/vehiculos/123`. Metodo, query params, headers (salvo `Host`/`Content-Length`, recalculados por `httpx`) y cuerpo se reenvian tal cual; la respuesta del backend (status, headers, cuerpo) se devuelve sin transformar.

## Correlacion de peticiones

El gateway genera (o respeta, si el cliente ya envio uno) un `X-Correlation-Id` y lo propaga tanto en su propia respuesta como en la peticion que reenvia al backend, para poder rastrear una peticion a traves de varios microservicios en los logs.

## Autenticacion (JWT)

Un middleware ASGI (`JWTAuthMiddleware`, mismo patron que `CorrelationIdMiddleware`) valida en cada peticion el JWT emitido por `POST /fleet/auth/login` (`fleet-management-service`). Usa la misma `JWT_SECRET_KEY` que ese servicio (debe coincidir en ambos `.env`).

- Sin token: `/health`, `/ready` y `POST /fleet/auth/login`.
- Con token (`Authorization: Bearer <token>`): todo lo demas. Sin token o con uno invalido/expirado devuelve `401` con el formato uniforme `{"codigo", "mensaje", "detalle"}`.
- Rol `ADMINISTRADOR` obligatorio para `PATCH`/`DELETE` sobre un vehiculo o conductor puntual (`/fleet/vehiculos/{id}`, `/fleet/conductores/{id}`); si el rol del token es `OPERADOR`, devuelve `403` (`ROL_NO_AUTORIZADO`). Crear (`POST`) y asignar/desasignar conductor quedan abiertos a ambos roles.

## Requisitos

- Python 3.12 (probado tambien con 3.13)
- Los cinco microservicios corriendo (para uso real; las pruebas no los necesitan)

No se usa Docker.

## Configuracion

```bash
cp .env.example .env
```

Ajusta las URLs de cada servicio en `.env` si corren en puertos distintos a los de por defecto.

## Instalacion local

```bash
python -m venv .venv
.venv\Scripts\activate      # en Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar el servicio

```bash
uvicorn app.main:app --reload --port 8080
```

Con los seis servicios corriendo, un cliente solo necesita hablar con `http://localhost:8080`.

## Pruebas

```bash
pytest --cov=app --cov-report=term-missing
```

Las pruebas no llaman a los microservicios reales: sobreescriben el `ProxyClient` con uno falso (para el proxy) y el cliente HTTP de `/ready` con `httpx.MockTransport` (para los health checks agregados).

## Endpoints propios

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness: hace `GET /health` a cada uno de los cinco microservicios |
| * | `/{prefijo}/{...}` | Proxy hacia el microservicio registrado bajo ese prefijo |
