# Proyecto-del-sector-logistica-transporte (Sistema de Gestión de flotas)

## FleetOps

FleetOps es un sistema de gestión de flotas orientado al sector de logística y transporte, diseñado con arquitectura de microservicios siguiendo el enfoque de arquitectura hexagonal (puertos y adaptadores) en cada servicio. Esto permite aislar la lógica de negocio de los detalles de infraestructura, facilitando la mantenibilidad, las pruebas y la evolución independiente de cada componente.

### Necesidades que resuelve

El sistema aborda cuatro necesidades críticas de una operación de transporte moderna:

- **Monitoreo en tiempo real de vehículos**
  Seguimiento continuo de posición, velocidad y estado operativo de cada unidad de la flota mediante ingestión de telemetría y notificación de eventos a los interesados (dashboards, alertas, otros servicios).

- **Optimización de rutas y asignación de cargas**
  Cálculo de rutas eficientes y asignación inteligente de cargas a vehículos disponibles, con algoritmos intercambiables según el contexto operativo (distancia, tiempo, restricciones de capacidad).

- **Mantenimiento predictivo**
  Análisis de variables de telemetría (kilometraje, horas de motor, patrones de uso) para anticipar fallas y generar alertas de mantenimiento antes de que ocurran averías.

- **Integración con sistemas de navegación**
  Comunicación con proveedores externos de mapas y navegación (Google Maps / OpenStreetMap), normalizando sus respuestas bajo una interfaz común del sistema.
