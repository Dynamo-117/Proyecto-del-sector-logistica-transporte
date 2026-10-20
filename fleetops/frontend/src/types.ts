export type Rol = "ADMINISTRADOR" | "OPERADOR";

export interface Usuario {
  id: string;
  email: string;
  rol: Rol;
  activo: boolean;
}

export type TipoVehiculo = "CAMION" | "FURGON" | "MOTO" | "VAN";
export type EstadoVehiculo = "DISPONIBLE" | "EN_RUTA" | "MANTENIMIENTO" | "INACTIVO";
export type EstadoConductor = "DISPONIBLE" | "ASIGNADO" | "INACTIVO";

export interface Vehiculo {
  id: string;
  placa: string;
  tipo: TipoVehiculo;
  capacidad_kg: number;
  estado: EstadoVehiculo;
  conductor_id: string | null;
  creado_en: string;
  actualizado_en: string;
}

export interface Conductor {
  id: string;
  nombre: string;
  licencia: string;
  estado: EstadoConductor;
  creado_en: string;
  actualizado_en: string;
}

// --- vehicle-tracking-service ---

export type EstadoMovimiento = "EN_MOVIMIENTO" | "DETENIDO";

export interface Telemetria {
  id: string;
  vehiculo_id: string;
  latitud: number;
  longitud: number;
  velocidad_kmh: number;
  timestamp: string;
}

export interface EstadoActual extends Telemetria {
  estado_movimiento: EstadoMovimiento;
}

export interface EventoTelemetria {
  vehiculo_id: string;
  latitud: number;
  longitud: number;
  velocidad_kmh: number;
  estado_movimiento: EstadoMovimiento;
  timestamp: string;
}

// --- route-optimization-service ---

export type EstadoRuta = "ACTIVA" | "COMPLETADA";

export interface Nodo {
  id: string;
  nombre: string;
  latitud: number;
  longitud: number;
}

export interface Conexion {
  id: string;
  nodo_origen_id: string;
  nodo_destino_id: string;
  distancia_km: number;
}

export interface RutaOptimizada {
  id: string;
  carga_id: string;
  vehiculo_id: string;
  vehiculo_placa: string | null;
  nodos: string[];
  distancia_km: number;
  estado: EstadoRuta;
  creado_en: string;
}

// --- predictive-maintenance-service ---

export type TipoAlerta = "CAMBIO_ACEITE" | "REVISION_GENERAL";
export type EstadoAlerta = "ACTIVA" | "RESUELTA";

export interface TipoMantenimientoInfo {
  nombre: string;
  descripcion: string;
  recomendacion: string;
  prioridad: "BAJA" | "MEDIA" | "ALTA";
  intervalo_km: number;
  intervalo_horas: number;
}

export interface AlertaMantenimiento {
  id: string;
  vehiculo_id: string;
  tipo: TipoAlerta;
  tipo_info: TipoMantenimientoInfo;
  estado: EstadoAlerta;
  kilometraje_km: number;
  horas_motor: number;
  generada_en: string;
  resuelta_en: string | null;
}

export interface IngestaConAlertas {
  kilometraje_km: number;
  horas_motor: number;
  alertas_generadas: AlertaMantenimiento[];
}

// --- navigation-integration-service ---

export interface Coordenada {
  latitud: number;
  longitud: number;
}

export interface RutaCalculada {
  origen: Coordenada;
  destino: Coordenada;
  distancia_km: number;
  duracion_min: number;
  puntos: Coordenada[];
}

// --- route-optimization-service: plan con paradas (Composite) ---

export interface ComponentePlan {
  tipo: "tramo" | "trayecto";
  nombre: string;
  distancia_km: number;
  cantidad_tramos: number;
  hijos: ComponentePlan[];
}

export interface PlanRuta {
  distancia_km: number;
  cantidad_tramos: number;
  paradas: string[];
  nodos: string[];
  estructura: ComponentePlan;
}

// --- api-gateway: resumen operativo (Facade) ---

export interface ResumenOperativo {
  flota: {
    disponible: boolean;
    total_vehiculos: number;
    vehiculos_por_estado: Record<string, number>;
    total_conductores: number;
    conductores_disponibles: number;
  };
  rutas: { disponible: boolean; rutas_activas: number; distancia_total_km: number };
  mantenimiento: { disponible: boolean; alertas_activas: number; vehiculos_con_alertas: number };
  tracking: { disponible: boolean; en_movimiento: number; detenidos: number; sin_telemetria: number };
  llamadas_internas: number;
  generado_en: string;
}

// --- fleet-management-service: estado de la mensajeria (Proxy) ---

export interface EstadoEventos {
  conectado: boolean;
  pendientes: number;
  publicados: number;
  descartados: number;
}
