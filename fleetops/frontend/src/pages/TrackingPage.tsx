import { useEffect, useState } from "react";
import { ApiRequestError, suscribirseSSE } from "../api/client";
import { listarVehiculos } from "../api/vehiculos";
import {
  ingestarTelemetria,
  listarHistorico,
  obtenerEstadoActual,
  rutaEventosVehiculo,
} from "../api/tracking";
import type { EstadoActual, EventoTelemetria, Telemetria, Vehiculo } from "../types";

const LAT_BASE = 4.711;
const LON_BASE = -74.0721;

function jitter(base: number, rango: number): number {
  return Number((base + (Math.random() - 0.5) * rango).toFixed(5));
}

export function TrackingPage() {
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [vehiculoId, setVehiculoId] = useState("");
  const [estado, setEstado] = useState<EstadoActual | null>(null);
  const [historico, setHistorico] = useState<Telemetria[]>([]);
  const [eventosVivo, setEventosVivo] = useState<EventoTelemetria[]>([]);
  const [enVivo, setEnVivo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const [latitud, setLatitud] = useState(jitter(LAT_BASE, 0.02));
  const [longitud, setLongitud] = useState(jitter(LON_BASE, 0.02));
  const [velocidad, setVelocidad] = useState(45);

  useEffect(() => {
    listarVehiculos()
      .then(setVehiculos)
      .catch((err) => setError(err instanceof ApiRequestError ? err.message : "No se pudieron cargar los vehiculos"));
  }, []);

  useEffect(() => {
    if (!enVivo || !vehiculoId) return;

    setEventosVivo([]);
    const detener = suscribirseSSE(
      rutaEventosVehiculo(vehiculoId),
      (data) => {
        try {
          setEventosVivo((prev) => [JSON.parse(data) as EventoTelemetria, ...prev].slice(0, 20));
        } catch {
          // ignora keep-alives / lineas no-JSON
        }
      },
      () => setError("Se perdio la conexion del stream en tiempo real"),
    );

    return detener;
  }, [enVivo, vehiculoId]);

  async function cargarEstadoYHistorico(id: string) {
    setError(null);
    try {
      const [estadoActual, hist] = await Promise.all([
        obtenerEstadoActual(id),
        listarHistorico(id, 10),
      ]);
      setEstado(estadoActual);
      setHistorico(hist);
    } catch (err) {
      setEstado(null);
      setHistorico([]);
      setError(
        err instanceof ApiRequestError
          ? err.message
          : "No se pudo consultar el estado del vehiculo",
      );
    }
  }

  async function handleEnviarLectura() {
    if (!vehiculoId) return;
    setEnviando(true);
    setError(null);
    try {
      await ingestarTelemetria({ vehiculo_id: vehiculoId, latitud, longitud, velocidad_kmh: velocidad });
      setLatitud(jitter(LAT_BASE, 0.02));
      setLongitud(jitter(LON_BASE, 0.02));
      await cargarEstadoYHistorico(vehiculoId);
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : "No se pudo enviar la lectura de telemetria",
      );
    } finally {
      setEnviando(false);
    }
  }

  function handleSeleccionar(id: string) {
    setVehiculoId(id);
    setEnVivo(false);
    setEstado(null);
    setHistorico([]);
    if (id) cargarEstadoYHistorico(id);
  }

  return (
    <div className="pagina">
      <h1>Tracking en tiempo real</h1>
      <p className="subtitulo">
        vehicle-tracking-service no tiene GPS reales conectados: usa el formulario para simular una
        lectura de posicion/velocidad para el vehiculo seleccionado.
      </p>

      <div className="tarjeta formulario-inline">
        <label>
          Vehiculo
          <select value={vehiculoId} onChange={(e) => handleSeleccionar(e.target.value)}>
            <option value="">Selecciona un vehiculo</option>
            {vehiculos.map((v) => (
              <option key={v.id} value={v.id}>
                {v.placa}
              </option>
            ))}
          </select>
        </label>
        <label>
          Latitud
          <input
            type="number"
            step="0.0001"
            value={latitud}
            onChange={(e) => setLatitud(Number(e.target.value))}
          />
        </label>
        <label>
          Longitud
          <input
            type="number"
            step="0.0001"
            value={longitud}
            onChange={(e) => setLongitud(Number(e.target.value))}
          />
        </label>
        <label>
          Velocidad (km/h)
          <input
            type="number"
            min="0"
            value={velocidad}
            onChange={(e) => setVelocidad(Number(e.target.value))}
          />
        </label>
        <button onClick={handleEnviarLectura} disabled={enviando || !vehiculoId}>
          {enviando ? "Enviando..." : "Simular lectura"}
        </button>
      </div>

      {error && <p className="mensaje-error">{error}</p>}

      {vehiculoId && (
        <>
          <div className="tarjeta">
            <div className="pagina__encabezado">
              <h2>Estado actual</h2>
              <button className="boton-secundario" onClick={() => setEnVivo((v) => !v)}>
                {enVivo ? "Detener stream en vivo" : "Ver stream en vivo (SSE)"}
              </button>
            </div>
            {estado ? (
              <p>
                <span className={`badge badge--${estado.estado_movimiento.toLowerCase()}`}>
                  {estado.estado_movimiento}
                </span>{" "}
                {estado.velocidad_kmh} km/h — ({estado.latitud}, {estado.longitud}) —{" "}
                {new Date(estado.timestamp).toLocaleTimeString()}
              </p>
            ) : (
              <p>
                Sin lecturas todavia para este vehiculo (envia una "lectura simulada" arriba, o
                corre <code>scripts/simulador_telemetria.py</code>).
              </p>
            )}
          </div>

          {enVivo && (
            <div className="tarjeta">
              <h2>Stream en vivo</h2>
              {eventosVivo.length === 0 && <p>Esperando eventos...</p>}
              <table className="tabla">
                <tbody>
                  {eventosVivo.map((ev, i) => (
                    <tr key={i}>
                      <td>{new Date(ev.timestamp).toLocaleTimeString()}</td>
                      <td>{ev.velocidad_kmh} km/h</td>
                      <td>
                        ({ev.latitud}, {ev.longitud})
                      </td>
                      <td>
                        <span className={`badge badge--${ev.estado_movimiento.toLowerCase()}`}>
                          {ev.estado_movimiento}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="tarjeta">
            <h2>Historico reciente</h2>
            <table className="tabla">
              <thead>
                <tr>
                  <th>Hora</th>
                  <th>Velocidad</th>
                  <th>Posicion</th>
                </tr>
              </thead>
              <tbody>
                {historico.map((h) => (
                  <tr key={h.id}>
                    <td>{new Date(h.timestamp).toLocaleTimeString()}</td>
                    <td>{h.velocidad_kmh} km/h</td>
                    <td>
                      ({h.latitud}, {h.longitud})
                    </td>
                  </tr>
                ))}
                {historico.length === 0 && (
                  <tr>
                    <td colSpan={3}>Sin historico todavia.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
