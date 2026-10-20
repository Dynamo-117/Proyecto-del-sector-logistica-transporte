import { apiFetch } from "./client";
import type { Coordenada, RutaCalculada } from "../types";

export type ProveedorNavegacion = "osrm" | "valhalla";

export function calcularRuta(
  origen: Coordenada,
  destino: Coordenada,
  proveedor: ProveedorNavegacion = "osrm",
): Promise<RutaCalculada> {
  return apiFetch<RutaCalculada>(`/navigation/rutas/calcular?proveedor=${proveedor}`, {
    method: "POST",
    body: JSON.stringify({ origen, destino }),
  });
}
