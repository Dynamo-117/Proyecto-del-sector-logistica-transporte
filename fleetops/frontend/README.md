# FleetOps · Frontend

Interfaz web de FleetOps: login con JWT y una pagina por cada uno de los 6 microservicios (vehiculos/conductores/asignacion, tracking en tiempo real, optimizacion de rutas, mantenimiento predictivo y navegacion/OSRM). Consume exclusivamente el `api-gateway` (nunca habla directo con los microservicios).

No es un microservicio backend, por eso vive fuera de `services/`.

## Stack

React + TypeScript + Vite. Sin framework de UI: CSS plano (`src/index.css`). Enrutamiento con `react-router-dom`.

## Requisitos

- Node.js 20+ y npm
- El `api-gateway` corriendo. Para que **todas** las paginas funcionen (no solo Vehiculos/Conductores) hacen falta los 6 microservicios corriendo, PostgreSQL y RabbitMQ. Ver el README de la raiz de `fleetops/` para levantar todo el backend.
  - `vehicle-tracking-service` ademas necesita la extension **TimescaleDB** instalada en Postgres — sin ella, la pagina de Tracking sigue cargando pero el gateway devuelve `502` al consultarla.
  - `navigation-integration-service` necesita salida a internet (consulta el servidor publico de OSRM).
- Al menos un usuario ADMINISTRADOR creado (`python -m scripts.crear_usuario_admin` en `services/fleet-management-service`) para poder iniciar sesion.

No se usa Docker en ningun punto del proyecto.

## Instalacion y ejecucion

```bash
cd frontend
npm install
cp .env.example .env   # ajusta VITE_API_URL si el gateway no corre en localhost:8080
npm run dev
```

La app queda disponible en `http://localhost:5173` (puerto por defecto de Vite).

## Configuracion

| Variable | Descripcion | Por defecto |
|---|---|---|
| `VITE_API_URL` | Base URL del `api-gateway` | `http://localhost:8080` |

## Estructura

```
src/
├── api/          # cliente fetch + funciones por dominio (una por microservicio)
│   ├── client.ts       # fetch autenticado + lector de SSE (suscribirseSSE)
│   ├── auth.ts          # fleet-management-service: /auth
│   ├── vehiculos.ts      # fleet-management-service: /vehiculos
│   ├── conductores.ts    # fleet-management-service: /conductores
│   ├── tracking.ts       # vehicle-tracking-service
│   ├── routing.ts        # route-optimization-service
│   ├── maintenance.ts    # predictive-maintenance-service
│   └── navigation.ts     # navigation-integration-service
├── auth/         # AuthContext (JWT en localStorage) + ProtectedRoute
├── components/   # Header, Layout
├── pages/        # LoginPage, VehiculosPage, ConductoresPage, AsignacionPage,
│                 # TrackingPage, RoutingPage, MaintenancePage, NavigationPage
├── types.ts
├── App.tsx       # rutas
└── main.tsx
```

## Paginas

| Pagina | Ruta | Microservicio detras | Que hace |
|---|---|---|---|
| Vehiculos | `/vehiculos` | fleet-management-service | CRUD de vehiculos |
| Conductores | `/conductores` | fleet-management-service | CRUD de conductores |
| Asignar conductor | `/asignaciones` | fleet-management-service | Asignar/desasignar conductor a vehiculo |
| Tracking | `/tracking` | vehicle-tracking-service | Simular una lectura GPS, ver estado actual, historico y stream en vivo (SSE) |
| Rutas | `/rutas` | route-optimization-service | Crear nodos/conexiones del grafo, solicitar asignacion de carga (Dijkstra), ver rutas activas |
| Mantenimiento | `/mantenimiento` | predictive-maintenance-service | Registrar lectura de odometro, ver/completar alertas |
| Navegacion | `/navegacion` | navigation-integration-service | Calcular ruta entre dos coordenadas via OSRM |

### Nota sobre el stream en vivo (SSE) de Tracking

El `EventSource` nativo del navegador no permite mandar headers, y todas las rutas del gateway exigen `Authorization: Bearer <token>`. Por eso `src/api/client.ts` implementa `suscribirseSSE()` con `fetch` + lectura manual del stream en vez de `EventSource`.

## Flujo de autenticacion

1. `LoginPage` llama a `POST /fleet/auth/login` (via el gateway) con email/password.
2. El JWT devuelto se guarda en `localStorage` (`fleetops_token`) y se adjunta como `Authorization: Bearer <token>` en cada peticion posterior (`src/api/client.ts`).
3. `AuthContext` resuelve el usuario actual llamando a `GET /fleet/auth/me` al cargar la app o tras iniciar sesion.
4. `ProtectedRoute` redirige a `/login` si no hay token valido.
5. El header muestra email/rol del usuario y permite cerrar sesion (borra el token).
6. El boton "Eliminar" en vehiculos/conductores solo aparece si el rol es `ADMINISTRADOR` (el backend tambien lo exige — el frontend solo oculta la opcion, no reemplaza esa validacion).

## Build de produccion

```bash
npm run build
npm run preview
```
