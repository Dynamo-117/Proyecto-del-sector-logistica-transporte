import { apiFetch } from "./client";
import type { Coordenada, RutaCalculada } from "../types";

export function calcularRuta(origen: Coordenada, destino: Coordenada): Promise<RutaCalculada> {
  return apiFetch<RutaCalculada>("/navigation/rutas/calcular", {
    method: "POST",
    body: JSON.stringify({ origen, destino }),
  });
}
