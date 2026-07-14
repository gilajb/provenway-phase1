import { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// Marketing page
import Landing from "./pages/Landing";

// Auth pages
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import VerifyEmail from "./pages/auth/VerifyEmail";

// Main app pages
import FeedPage from "./pages/main/FeedPage";
import ProfilePage from "./pages/main/ProfilePage";
import ProjectPage from "./pages/main/ProjectPage";
import SearchPage from "./pages/main/SearchPage";

// Layout wrappers
import AuthLayout from "./components/layout/AuthLayout";
import AppLayout from "./components/layout/AppLayout";
import ProtectedRoute from "./components/layout/ProtectedRoute";

import { useAuthStore } from "./stores/authStore";

export default function App() {
  // Rebuild the session from the persisted refresh token (if any) once,
  // on first mount. See stores/authStore.js hydrate().
  useEffect(() => {
    useAuthStore.getState().hydrate();
  }, []);

  return (
    <Routes>
      {/* ── Unauthenticated routes ────────────────────────────────────────── */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
      </Route>

      {/* ── Authenticated routes ──────────────────────────────────────────── */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/feed" element={<FeedPage />} />
          <Route path="/profile/:id" element={<ProfilePage />} />
          <Route path="/projects/:id" element={<ProjectPage />} />
          <Route path="/search" element={<SearchPage />} />
        </Route>
      </Route>

      {/* ── Public marketing page ────────────────────────────────────────── */}
      <Route path="/" element={<Landing />} />

      {/* ── Default redirect ──────────────────────────────────────────────── */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
