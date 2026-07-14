/**
 * src/components/layout/ProtectedRoute.jsx
 * ─────────────────────────────────────────
 * Redirects unauthenticated users to /login.
 * Wraps authenticated route groups in App.jsx.
 */
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function ProtectedRoute() {
  const { isAuthenticated, isHydrating } = useAuth();
  const location = useLocation();

  if (isHydrating) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
        <div style={{ color: "var(--color-on-surface-variant)", fontFamily: "var(--font-family-base)" }}>
          Loading…
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
