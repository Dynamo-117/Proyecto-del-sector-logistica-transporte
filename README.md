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

### Objetivo General
Diseñar e implementar un sistema de gestión de flotas para el sector de logística y transporte, basado en una arquitectura de microservicios con enfoque hexagonal, que integre monitoreo en tiempo real, optimización de rutas, mantenimiento predictivo e integración con sistemas de navegación, aplicando patrones de diseño GoF, prácticas de calidad de software y un pipeline de integración y entrega continua.
### Objetivos Especificos
-  Diseñar una arquitectura de microservicios con enfoque hexagonal (puertos y adaptadores) que garantice bajo acoplamiento, alta cohesión y separación clara entre la lógica de negocio y la infraestructura de cada servicio.
-   Implementar un módulo de monitoreo en tiempo real que capture y notifique la posición, el estado y los eventos operativos de cada vehículo de la flota.
- 	Desarrollar un módulo de optimización de rutas y asignación de cargas que permita comparar y seleccionar estrategias de cálculo según el contexto operativo.
- 	Construir un módulo de mantenimiento predictivo capaz de generar alertas a partir del análisis de variables de telemetría de los vehículos.
- 	Integrar el sistema con proveedores externos de navegación, normalizando sus respuestas bajo una interfaz común e independiente del proveedor.
- 	Aplicar al menos ocho patrones de diseño GoF, con un mínimo de dos por categoría (creacional, estructural y de comportamiento), justificando su elección y su aporte a la mantenibilidad del sistema.
- 	Documentar las decisiones arquitectónicas del proyecto mediante Architecture Decision Records (ADR) y diagramas UML que respalden el diseño implementado.
- 	Establecer una suite de pruebas automatizadas con una cobertura de código igual o superior al 80%, que permita refactorizar el sistema con confianza.
- 	Configurar un flujo de control de versiones con Git y un pipeline de integración y entrega continua (CI/CD) que automatice la construcción, las pruebas y el despliegue del sistema.
- 	Implementar monitoreo y logging centralizado (Prometheus, Grafana y Loki) que permita observar el estado y el comportamiento del sistema en tiempo de ejecución.
