import { useEffect, useState, type FormEvent } from "react";
import { ApiRequestError } from "../api/client";
import {
  crearConexion,
  crearNodo,
  listarNodos,
  listarRutas,
  solicitarAsignacion,
} from "../api/routing";
import type { Nodo, RutaOptimizada } from "../types";

export function RoutingPage() {
  const [nodos, setNodos] = useState<Nodo[]>([]);
  const [rutas, setRutas] = useState<RutaOptimizada[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);

  const [nombreNodo, setNombreNodo] = useState("");
  const [latNodo, setLatNodo] = useState("");
  const [lonNodo, setLonNodo] = useState("");

  const [origenConexion, setOrigenConexion] = useState("");
  const [destinoConexion, setDestinoConexion] = useState("");
  const [distanciaConexion, setDistanciaConexion] = useState("");

  const [origenCarga, setOrigenCarga] = useState("");
  const [destinoCarga, setDestinoCarga] = useState("");
  const [pesoCarga, setPesoCarga] = useState("");
  const [volumenCarga, setVolumenCarga] = useState("");

  const [enviando, setEnviando] = useState(false);

  async function cargar() {
    try {
      const [n, r] = await Promise.all([listarNodos(), listarRutas()]);
      setNodos(n);
      setRutas(r);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo cargar el grafo de rutas");
    }
  }

  useEffect(() => {
    cargar();
  }, []);

  function nombreNodoPorId(id: string): string {
    return nodos.find((n) => n.id === id)?.nombre ?? id;
  }

  async function handleCrearNodo(evento: FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await crearNodo({ nombre: nombreNodo, latitud: Number(latNodo), longitud: Number(lonNodo) });
      setNombreNodo("");
      setLatNodo("");
      setLonNodo("");
      await cargar();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo crear el nodo");
    } finally {
      setEnviando(false);
    }
  }

  async function handleCrearConexion(evento: FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await crearConexion(origenConexion, destinoConexion, Number(distanciaConexion));
      setDistanciaConexion("");
      setMensaje("Conexion creada.");
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo crear la conexion");
    } finally {
      setEnviando(false);
    }
  }

  async function handleSolicitarCarga(evento: FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    setMensaje(null);
    try {
      const ruta = await solicitarAsignacion({
        origen_nodo_id: origenCarga,
        destino_nodo_id: destinoCarga,
        peso_kg: Number(pesoCarga),
        volumen_m3: Number(volumenCarga),
      });
      setMensaje(
        `Ruta asignada: ${ruta.distancia_km} km, vehiculo ${ruta.vehiculo_placa ?? ruta.vehiculo_id}.`,
      );
      setPesoCarga("");
      setVolumenCarga("");
      await cargar();
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : "No se pudo solicitar la asignacion",
      );
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="pagina">
      <h1>Optimizacion de rutas</h1>

      {error && <p className="mensaje-error">{error}</p>}
      {mensaje && <p className="mensaje-exito">{mensaje}</p>}

      <div className="tarjeta">
        <h2>Nodos del grafo</h2>
        <form className="formulario-inline" onSubmit={handleCrearNodo}>
          <label>
            Nombre
            <input value={nombreNodo} onChange={(e) => setNombreNodo(e.target.value)} required />
          </label>
          <label>
            Latitud
            <input
              type="number"
              step="0.0001"
              value={latNodo}
              onChange={(e) => setLatNodo(e.target.value)}
              required
            />
          </label>
          <label>
            Longitud
            <input
              type="number"
              step="0.0001"
              value={lonNodo}
              onChange={(e) => setLonNodo(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={enviando}>
            Crear nodo
          </button>
        </form>

        <table className="tabla">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Latitud</th>
              <th>Longitud</th>
            </tr>
          </thead>
          <tbody>
            {nodos.map((n) => (
              <tr key={n.id}>
                <td>{n.nombre}</td>
                <td>{n.latitud}</td>
                <td>{n.longitud}</td>
              </tr>
            ))}
            {nodos.length === 0 && (
              <tr>
                <td colSpan={3}>No hay nodos todavia.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="tarjeta">
        <h2>Conectar dos nodos</h2>
        <form className="formulario-inline" onSubmit={handleCrearConexion}>
          <label>
            Origen
            <select value={origenConexion} onChange={(e) => setOrigenConexion(e.target.value)} required>
              <option value="">Selecciona</option>
              {nodos.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.nombre}
                </option>
              ))}
            </select>
          </label>
          <label>
            Destino
            <select value={destinoConexion} onChange={(e) => setDestinoConexion(e.target.value)} required>
              <option value="">Selecciona</option>
              {nodos.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.nombre}
                </option>
              ))}
            </select>
          </label>
          <label>
            Distancia (km)
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={distanciaConexion}
              onChange={(e) => setDistanciaConexion(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={enviando || nodos.length < 2}>
            Conectar
          </button>
        </form>
      </div>

      <div className="tarjeta">
        <h2>Solicitar asignacion de carga</h2>
        <form className="formulario-inline" onSubmit={handleSolicitarCarga}>
          <label>
            Origen
            <select value={origenCarga} onChange={(e) => setOrigenCarga(e.target.value)} required>
              <option value="">Selecciona</option>
              {nodos.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.nombre}
                </option>
              ))}
            </select>
          </label>
          <label>
            Destino
            <select value={destinoCarga} onChange={(e) => setDestinoCarga(e.target.value)} required>
              <option value="">Selecciona</option>
              {nodos.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.nombre}
                </option>
              ))}
            </select>
          </label>
          <label>
            Peso (kg)
            <input
              type="number"
              min="1"
              value={pesoCarga}
              onChange={(e) => setPesoCarga(e.target.value)}
              required
            />
          </label>
          <label>
            Volumen (m3)
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={volumenCarga}
              onChange={(e) => setVolumenCarga(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={enviando || nodos.length < 2}>
            Asignar
          </button>
        </form>
        <p className="subtitulo">
          Requiere al menos un vehiculo DISPONIBLE (creado en Vehiculos, ya sincronizado por
          eventos).
        </p>
      </div>

      <div className="tarjeta">
        <h2>Rutas activas</h2>
        <table className="tabla">
          <thead>
            <tr>
              <th>Vehiculo</th>
              <th>Distancia</th>
              <th>Nodos</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {rutas.map((r) => (
              <tr key={r.id}>
                <td>{r.vehiculo_placa ?? r.vehiculo_id}</td>
                <td>{r.distancia_km} km</td>
                <td>{r.nodos.map(nombreNodoPorId).join(" -> ")}</td>
                <td>
                  <span className={`badge badge--${r.estado.toLowerCase()}`}>{r.estado}</span>
                </td>
              </tr>
            ))}
            {rutas.length === 0 && (
              <tr>
                <td colSpan={4}>No hay rutas activas.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
