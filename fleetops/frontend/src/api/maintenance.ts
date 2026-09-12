import { apiFetch } from "./client";
import type { AlertaMantenimiento, IngestaConAlertas } from "../types";

export interface LecturaOdometroPayload {
  vehiculo_id: string;
  kilometraje_km: number;
  horas_motor: number;
}

export function registrarLectura(payload: LecturaOdometroPayload): Promise<IngestaConAlertas> {
  return apiFetch<IngestaConAlertas>("/maintenance/lecturas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listarAlertasActivas(vehiculoId: string): Promise<AlertaMantenimiento[]> {
  return apiFetch<AlertaMantenimiento[]>(`/maintenance/vehiculos/${vehiculoId}/alertas`);
}

export function completarAlerta(alertaId: string): Promise<AlertaMantenimiento> {
  return apiFetch<AlertaMantenimiento>(`/maintenance/alertas/${alertaId}/completar`, {
    method: "POST",
  });
}
