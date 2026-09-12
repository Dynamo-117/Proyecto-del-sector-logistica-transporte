import { apiFetch } from "./client";
import type { TipoVehiculo, Vehiculo } from "../types";

export function listarVehiculos(): Promise<Vehiculo[]> {
  return apiFetch<Vehiculo[]>("/fleet/vehiculos");
}

export interface VehiculoCreatePayload {
  placa: string;
  tipo: TipoVehiculo;
  capacidad_kg: number;
}

export function crearVehiculo(payload: VehiculoCreatePayload): Promise<Vehiculo> {
  return apiFetch<Vehiculo>("/fleet/vehiculos", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function eliminarVehiculo(id: string): Promise<void> {
  return apiFetch<void>(`/fleet/vehiculos/${id}`, { method: "DELETE" });
}

export function asignarConductor(vehiculoId: string, conductorId: string): Promise<Vehiculo> {
  return apiFetch<Vehiculo>(`/fleet/vehiculos/${vehiculoId}/asignar-conductor`, {
    method: "POST",
    body: JSON.stringify({ conductor_id: conductorId }),
  });
}

export function desasignarConductor(vehiculoId: string): Promise<Vehiculo> {
  return apiFetch<Vehiculo>(`/fleet/vehiculos/${vehiculoId}/desasignar-conductor`, {
    method: "POST",
  });
}
