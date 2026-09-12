import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ApiRequestError } from "../api/client";
import { listarConductores } from "../api/conductores";
import { asignarConductor, desasignarConductor, listarVehiculos } from "../api/vehiculos";
import type { Conductor, Vehiculo } from "../types";

export function AsignacionPage() {
  const [searchParams] = useSearchParams();

  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [conductores, setConductores] = useState<Conductor[]>([]);
  const [vehiculoId, setVehiculoId] = useState(searchParams.get("vehiculo") ?? "");
  const [conductorId, setConductorId] = useState("");
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function cargar() {
    const [listaVehiculos, listaConductores] = await Promise.all([
      listarVehiculos(),
      listarConductores(),
    ]);
    setVehiculos(listaVehiculos);
    setConductores(listaConductores);
  }

  useEffect(() => {
    cargar();
  }, []);

  const vehiculoSeleccionado = vehiculos.find((v) => v.id === vehiculoId);

  async function handleAsignar() {
    if (!vehiculoId || !conductorId) return;
    setEnviando(true);
    setError(null);
    setMensaje(null);
    try {
      await asignarConductor(vehiculoId, conductorId);
      setMensaje("Conductor asignado correctamente.");
      setConductorId("");
      await cargar();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo asignar el conductor");
    } finally {
      setEnviando(false);
    }
  }

  async function handleDesasignar() {
    if (!vehiculoId) return;
    setEnviando(true);
    setError(null);
    setMensaje(null);
    try {
      await desasignarConductor(vehiculoId);
      setMensaje("Conductor desasignado.");
      await cargar();
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : "No se pudo desasignar el conductor",
      );
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="pagina">
      <h1>Asignar conductor a vehiculo</h1>

      <div className="tarjeta formulario-inline">
        <label>
          Vehiculo
          <select value={vehiculoId} onChange={(e) => setVehiculoId(e.target.value)}>
            <option value="">Selecciona un vehiculo</option>
            {vehiculos.map((vehiculo) => (
              <option key={vehiculo.id} value={vehiculo.id}>
                {vehiculo.placa} ({vehiculo.estado})
              </option>
            ))}
          </select>
        </label>

        <label>
          Conductor
          <select value={conductorId} onChange={(e) => setConductorId(e.target.value)}>
            <option value="">Selecciona un conductor</option>
            {conductores.map((conductor) => (
              <option key={conductor.id} value={conductor.id}>
                {conductor.nombre} ({conductor.estado})
              </option>
            ))}
          </select>
        </label>

        <div className="formulario-inline__acciones">
          <button onClick={handleAsignar} disabled={enviando || !vehiculoId || !conductorId}>
            Asignar
          </button>
          <button
            className="boton-secundario"
            onClick={handleDesasignar}
            disabled={enviando || !vehiculoId || !vehiculoSeleccionado?.conductor_id}
          >
            Desasignar
          </button>
        </div>
      </div>

      {mensaje && <p className="mensaje-exito">{mensaje}</p>}
      {error && <p className="mensaje-error">{error}</p>}
    </div>
  );
}
