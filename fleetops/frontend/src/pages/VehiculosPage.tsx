import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { ApiRequestError } from "../api/client";
import { listarConductores } from "../api/conductores";
import { crearVehiculo, eliminarVehiculo, listarVehiculos } from "../api/vehiculos";
import { useAuth } from "../auth/AuthContext";
import type { Conductor, TipoVehiculo, Vehiculo } from "../types";

const TIPOS: TipoVehiculo[] = ["CAMION", "FURGON", "MOTO", "VAN"];

export function VehiculosPage() {
  const { usuario } = useAuth();
  const esAdministrador = usuario?.rol === "ADMINISTRADOR";

  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [conductores, setConductores] = useState<Conductor[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [placa, setPlaca] = useState("");
  const [tipo, setTipo] = useState<TipoVehiculo>("CAMION");
  const [capacidad, setCapacidad] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function cargar() {
    setCargando(true);
    setError(null);
    try {
      const [listaVehiculos, listaConductores] = await Promise.all([
        listarVehiculos(),
        listarConductores(),
      ]);
      setVehiculos(listaVehiculos);
      setConductores(listaConductores);
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : "No se pudieron cargar los vehiculos",
      );
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    cargar();
  }, []);

  function nombreConductor(conductorId: string | null): string {
    if (!conductorId) return "Sin asignar";
    return conductores.find((c) => c.id === conductorId)?.nombre ?? conductorId;
  }

  async function handleCrear(evento: FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await crearVehiculo({ placa, tipo, capacidad_kg: Number(capacidad) });
      setPlaca("");
      setCapacidad("");
      setTipo("CAMION");
      setMostrarFormulario(false);
      await cargar();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo crear el vehiculo");
    } finally {
      setEnviando(false);
    }
  }

  async function handleEliminar(id: string) {
    if (!window.confirm("¿Eliminar este vehiculo?")) return;
    setError(null);
    try {
      await eliminarVehiculo(id);
      await cargar();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo eliminar el vehiculo");
    }
  }

  return (
    <div className="pagina">
      <div className="pagina__encabezado">
        <h1>Vehiculos</h1>
        <button onClick={() => setMostrarFormulario((valor) => !valor)}>
          {mostrarFormulario ? "Cancelar" : "Nuevo vehiculo"}
        </button>
      </div>

      {mostrarFormulario && (
        <form className="tarjeta formulario-inline" onSubmit={handleCrear}>
          <label>
            Placa
            <input value={placa} onChange={(e) => setPlaca(e.target.value)} required />
          </label>
          <label>
            Tipo
            <select value={tipo} onChange={(e) => setTipo(e.target.value as TipoVehiculo)}>
              {TIPOS.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <label>
            Capacidad (kg)
            <input
              type="number"
              min="1"
              step="0.1"
              value={capacidad}
              onChange={(e) => setCapacidad(e.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={enviando}>
            {enviando ? "Creando..." : "Crear"}
          </button>
        </form>
      )}

      {error && <p className="mensaje-error">{error}</p>}

      {cargando ? (
        <p>Cargando...</p>
      ) : (
        <table className="tabla">
          <thead>
            <tr>
              <th>Placa</th>
              <th>Tipo</th>
              <th>Capacidad (kg)</th>
              <th>Estado</th>
              <th>Conductor asignado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {vehiculos.map((vehiculo) => (
              <tr key={vehiculo.id}>
                <td>{vehiculo.placa}</td>
                <td>{vehiculo.tipo}</td>
                <td>{vehiculo.capacidad_kg}</td>
                <td>
                  <span className={`badge badge--${vehiculo.estado.toLowerCase()}`}>
                    {vehiculo.estado}
                  </span>
                </td>
                <td>{nombreConductor(vehiculo.conductor_id)}</td>
                <td className="tabla__acciones">
                  <Link to={`/asignaciones?vehiculo=${vehiculo.id}`}>Asignar conductor</Link>
                  {esAdministrador && (
                    <button
                      className="boton-peligro"
                      onClick={() => handleEliminar(vehiculo.id)}
                    >
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {vehiculos.length === 0 && (
              <tr>
                <td colSpan={6}>No hay vehiculos registrados.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
