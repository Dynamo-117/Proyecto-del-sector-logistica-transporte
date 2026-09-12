import { useEffect, useState, type FormEvent } from "react";
import { ApiRequestError } from "../api/client";
import { crearConductor, eliminarConductor, listarConductores } from "../api/conductores";
import { useAuth } from "../auth/AuthContext";
import type { Conductor } from "../types";

export function ConductoresPage() {
  const { usuario } = useAuth();
  const esAdministrador = usuario?.rol === "ADMINISTRADOR";

  const [conductores, setConductores] = useState<Conductor[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [nombre, setNombre] = useState("");
  const [licencia, setLicencia] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function cargar() {
    setCargando(true);
    setError(null);
    try {
      setConductores(await listarConductores());
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : "No se pudieron cargar los conductores",
      );
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    cargar();
  }, []);

  async function handleCrear(evento: FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await crearConductor({ nombre, licencia });
      setNombre("");
      setLicencia("");
      setMostrarFormulario(false);
      await cargar();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo crear el conductor");
    } finally {
      setEnviando(false);
    }
  }

  async function handleEliminar(id: string) {
    if (!window.confirm("¿Eliminar este conductor?")) return;
    setError(null);
    try {
      await eliminarConductor(id);
      await cargar();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo eliminar el conductor");
    }
  }

  return (
    <div className="pagina">
      <div className="pagina__encabezado">
        <h1>Conductores</h1>
        <button onClick={() => setMostrarFormulario((valor) => !valor)}>
          {mostrarFormulario ? "Cancelar" : "Nuevo conductor"}
        </button>
      </div>

      {mostrarFormulario && (
        <form className="tarjeta formulario-inline" onSubmit={handleCrear}>
          <label>
            Nombre
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          </label>
          <label>
            Licencia
            <input value={licencia} onChange={(e) => setLicencia(e.target.value)} required />
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
              <th>Nombre</th>
              <th>Licencia</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {conductores.map((conductor) => (
              <tr key={conductor.id}>
                <td>{conductor.nombre}</td>
                <td>{conductor.licencia}</td>
                <td>
                  <span className={`badge badge--${conductor.estado.toLowerCase()}`}>
                    {conductor.estado}
                  </span>
                </td>
                <td className="tabla__acciones">
                  {esAdministrador && (
                    <button
                      className="boton-peligro"
                      onClick={() => handleEliminar(conductor.id)}
                    >
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {conductores.length === 0 && (
              <tr>
                <td colSpan={4}>No hay conductores registrados.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
