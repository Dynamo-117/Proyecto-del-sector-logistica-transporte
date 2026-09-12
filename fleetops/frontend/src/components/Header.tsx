import { NavLink } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function Header() {
  const { usuario, logout } = useAuth();

  return (
    <header className="app-header">
      <div className="app-header__marca">FleetOps</div>

      <nav className="app-header__nav">
        <NavLink to="/vehiculos">Vehiculos</NavLink>
        <NavLink to="/conductores">Conductores</NavLink>
        <NavLink to="/asignaciones">Asignar conductor</NavLink>
        <NavLink to="/tracking">Tracking</NavLink>
        <NavLink to="/rutas">Rutas</NavLink>
        <NavLink to="/mantenimiento">Mantenimiento</NavLink>
        <NavLink to="/navegacion">Navegacion</NavLink>
      </nav>

      {usuario && (
        <div className="app-header__usuario">
          <span>
            {usuario.email} <span className="badge">{usuario.rol}</span>
          </span>
          <button className="boton-secundario" onClick={logout}>
            Cerrar sesion
          </button>
        </div>
      )}
    </header>
  );
}
