import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { Layout } from "./components/Layout";
import { AsignacionPage } from "./pages/AsignacionPage";
import { ConductoresPage } from "./pages/ConductoresPage";
import { LoginPage } from "./pages/LoginPage";
import { MaintenancePage } from "./pages/MaintenancePage";
import { NavigationPage } from "./pages/NavigationPage";
import { RoutingPage } from "./pages/RoutingPage";
import { TrackingPage } from "./pages/TrackingPage";
import { VehiculosPage } from "./pages/VehiculosPage";

export function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route index element={<Navigate to="/vehiculos" replace />} />
            <Route path="/vehiculos" element={<VehiculosPage />} />
            <Route path="/conductores" element={<ConductoresPage />} />
            <Route path="/asignaciones" element={<AsignacionPage />} />
            <Route path="/tracking" element={<TrackingPage />} />
            <Route path="/rutas" element={<RoutingPage />} />
            <Route path="/mantenimiento" element={<MaintenancePage />} />
            <Route path="/navegacion" element={<NavigationPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
