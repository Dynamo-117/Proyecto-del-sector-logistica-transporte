import { useEffect, useState, type FormEvent } from "react";
import { ApiRequestError } from "../api/client";
import { completarAlerta, listarAlertasActivas, registrarLectura } from "../api/maintenance";
import { listarVehiculos } from "../api/vehiculos";
import type { AlertaMantenimiento, Vehiculo } from "../types";

export function MaintenancePage() {
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [vehiculoId, setVehiculoId] = useState("");
  const [kilometraje, setKilometraje] = useState("");
  const [horasMotor, setHorasMotor] = useState("");
  const [alertas, setAlertas] = useState<AlertaMantenimiento[]>([]);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    listarVehiculos()
      .then(setVehiculos)
      .catch((err) =>
        setError(err instanceof ApiRequestError ? err.message : "No se pudieron cargar los vehiculos"),
      );
  }, []);

  async function cargarAlertas(id: string) {
    try {
      setAlertas(await listarAlertasActivas(id));
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudieron cargar las alertas");
    }
  }

  function handleSeleccionar(id: string) {
    setVehiculoId(id);
    setAlertas([]);
    setMensaje(null);
    if (id) cargarAlertas(id);
  }

  async function handleRegistrarLectura(evento: FormEvent) {
    evento.preventDefault();
    setEnviando(true);
    setError(null);
    setMensaje(null);
    try {
      const resultado = await registrarLectura({
        vehiculo_id: vehiculoId,
        kilometraje_km: Number(kilometraje),
        horas_motor: Number(horasMotor),
      });
      setMensaje(
        resultado.alertas_generadas.length > 0
          ? `Lectura registrada. Se generaron ${resultado.alertas_generadas.length} alerta(s) nueva(s).`
          : "Lectura registrada. Sin alertas nuevas.",
      );
      await cargarAlertas(vehiculoId);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo registrar la lectura");
    } finally {
      setEnviando(false);
    }
  }

  async function handleCompletar(alertaId: string) {
    setError(null);
    try {
      await completarAlerta(alertaId);
      await cargarAlertas(vehiculoId);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "No se pudo completar la alerta");
    }
  }

  return (
    <div className="pagina">
      <h1>Mantenimiento predictivo</h1>
      <p className="subtitulo">
        Umbrales fijos: CAMBIO_ACEITE cada 10.000 km / 300 h de motor, REVISION_GENERAL cada
        20.000 km / 600 h.
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
      </div>

      {error && <p className="mensaje-error">{error}</p>}
      {mensaje && <p className="mensaje-exito">{mensaje}</p>}

      {vehiculoId && (
        <>
          <div className="tarjeta">
            <h2>Registrar lectura de odometro</h2>
            <form className="formulario-inline" onSubmit={handleRegistrarLectura}>
              <label>
                Kilometraje (km)
                <input
                  type="number"
                  min="0"
                  value={kilometraje}
                  onChange={(e) => setKilometraje(e.target.value)}
                  required
                />
              </label>
              <label>
                Horas de motor
                <input
                  type="number"
                  min="0"
                  value={horasMotor}
                  onChange={(e) => setHorasMotor(e.target.value)}
                  required
                />
              </label>
              <button type="submit" disabled={enviando}>
                {enviando ? "Registrando..." : "Registrar"}
              </button>
            </form>
          </div>

          <div className="tarjeta">
            <h2>Alertas activas</h2>
            <table className="tabla">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Kilometraje</th>
                  <th>Horas motor</th>
                  <th>Generada</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {alertas.map((a) => (
                  <tr key={a.id}>
                    <td>{a.tipo}</td>
                    <td>{a.kilometraje_km} km</td>
                    <td>{a.horas_motor} h</td>
                    <td>{new Date(a.generada_en).toLocaleString()}</td>
                    <td>
                      <button className="boton-secundario" onClick={() => handleCompletar(a.id)}>
                        Completar
                      </button>
                    </td>
                  </tr>
                ))}
                {alertas.length === 0 && (
                  <tr>
                    <td colSpan={5}>Sin alertas activas para este vehiculo.</td>
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
