/**
 * src/hooks/useAuth.js
 * ─────────────────────
 * Convenience re-export of the auth store as a hook. Components can
 * keep writing `const { user, login, logout } = useAuth();` — this
 * returns the full store (state + actions), backed by Zustand rather
 * than React Context.
 */
export { useAuthStore as useAuth } from "../stores/authStore";
