import { apiFetch } from "./client";
import type { EstadoActual, Telemetria } from "../types";

export interface TelemetriaIngestaPayload {
  vehiculo_id: string;
  latitud: number;
  longitud: number;
  velocidad_kmh: number;
}

export function ingestarTelemetria(payload: TelemetriaIngestaPayload): Promise<Telemetria> {
  return apiFetch<Telemetria>("/tracking/telemetria", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function obtenerEstadoActual(vehiculoId: string): Promise<EstadoActual> {
  return apiFetch<EstadoActual>(`/tracking/vehiculos/${vehiculoId}/estado`);
}

export function listarHistorico(vehiculoId: string, limit = 20): Promise<Telemetria[]> {
  return apiFetch<Telemetria[]>(`/tracking/vehiculos/${vehiculoId}/historico?limit=${limit}`);
}

export function rutaEventosVehiculo(vehiculoId: string): string {
  return `/tracking/vehiculos/${vehiculoId}/eventos`;
}
