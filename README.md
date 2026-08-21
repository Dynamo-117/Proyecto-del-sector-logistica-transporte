# Proyecto-del-sector-logistica-transporte
## Sistema de Gestión de flotas

FleetOps es un sistema de gestión de flotas orientado al sector de logística y transporte, diseñado con arquitectura de microservicios siguiendo el enfoque de arquitectura hexagonal (puertos y adaptadores) en cada servicio, lo que permite aislar la lógica de negocio de los detalles de infraestructura y facilita la mantenibilidad, las pruebas y la evolución independiente de cada componente.

El sistema resuelve cuatro necesidades críticas de una operación de transporte moderna:

Monitoreo en tiempo real de vehículos: seguimiento continuo de posición, velocidad y estado operativo de cada unidad de la flota mediante ingestión de telemetría y notificación de eventos a los interesados (dashboards, alertas, otros servicios).
Optimización de rutas y asignación de cargas: cálculo de rutas eficientes y asignación inteligente de cargas a vehículos disponibles, con algoritmos intercambiables según el contexto operativo (distancia, tiempo, restricciones de capacidad).
Mantenimiento predictivo: análisis de variables de telemetría (kilometraje, horas de motor, patrones de uso) para anticipar fallas y generar alertas de mantenimiento antes de que ocurran averías.
Integración con sistemas de navegación: comunicación con proveedores externos de mapas y navegación (Google Maps / OpenStreetMap), normalizando sus respuestas bajo una interfaz común del sistema.
