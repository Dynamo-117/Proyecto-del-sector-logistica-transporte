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

export interface AlertaMantenimiento {
  id: string;
  vehiculo_id: string;
  tipo: TipoAlerta;
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
