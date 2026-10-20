import { useEffect, useState } from "react";
import { ApiRequestError } from "../api/client";
import { obtenerEstadoEventos, reintentarEventos } from "../api/eventos";
import type { EstadoEventos as Estado } from "../types";

export function EstadoEventos({ refrescarCon }: { refrescarCon?: unknown }) {
  const [estado, setEstado] = useState<Estado | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function cargar() {
    try {
      setEstado(await obtenerEstadoEventos());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo consultar la mensajeria");
    }
  }

  async function handleReintentar() {
    await reintentarEventos().catch(() => null);
    await cargar();
  }

  useEffect(() => {
    cargar();
  }, [refrescarCon]);

  if (error) return <p className="mensaje-error">{error}</p>;
  if (!estado) return null;

  return (
    <div className="estado-eventos">
      <span className={`badge ${estado.conectado ? "badge--disponible" : "badge--mantenimiento"}`}>
        Mensajeria: {estado.conectado ? "RabbitMQ conectado" : "RabbitMQ no disponible"}
      </span>
      <span>
        {estado.pendientes} evento(s) pendiente(s) · {estado.publicados} entregado(s)
      </span>
      {estado.pendientes > 0 && (
        <button className="boton-secundario" onClick={handleReintentar}>
          Reintentar entrega
        </button>
      )}
    </div>
  );
}
