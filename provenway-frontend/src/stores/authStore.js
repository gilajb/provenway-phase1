/**
 * src/stores/authStore.js
 * ────────────────────────
 * Single source of truth for auth state: user, accessToken, refreshToken,
 * isAuthenticated, plus login()/logout()/register()/hydrate().
 *
 * Token storage model (Engineering Doc §6.2, adapted for a plain SPA
 * without an httpOnly-cookie-issuing backend):
 * - accessToken lives in memory only (this store's state), never
 *   persisted. It's gone on tab close or hard refresh by design — the
 *   401 interceptor in apiClient.js and hydrate() below silently rebuild
 *   it from the refresh token instead.
 * - refreshToken is persisted to sessionStorage, not localStorage. That
 *   keeps a page refresh from forcing a re-login while still clearing on
 *   tab/browser close and limiting the exposure window compared to
 *   localStorage. It's a pragmatic SPA compromise, not a substitute for
 *   a real httpOnly cookie — worth revisiting if the backend ever issues
 *   one directly.
 */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { apiClient } from "../lib/api/apiClient";
import { AUTH } from "../lib/api/endpoints";

// Single-flight guard for refreshAccessToken (module-level, not store
// state — it's plumbing, not app state). Without this, two concurrent
// callers (e.g. React StrictMode double-invoking App.jsx's hydrate()
// effect in dev) both read the same refreshToken and both call
// /auth/token/refresh/ with it. The backend rotates + blacklists on
// every refresh (ROTATE_REFRESH_TOKENS/BLACKLIST_AFTER_ROTATION), so
// the first call succeeds and the second necessarily 401s on the
// now-blacklisted token — and its catch block used to unconditionally
// clear the whole session, silently logging out a user who had just
// successfully authenticated seconds earlier.
let refreshPromise = null;

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      // True until hydrate() (called once from App.jsx on mount) finishes
      // trying to rebuild the session from the persisted refresh token.
      isHydrating: true,

      async login(email, password) {
        const data = await apiClient.post(AUTH.LOGIN, { email, password });
        set({
          accessToken: data.access,
          refreshToken: data.refresh,
          user: data.user ?? null,
          isAuthenticated: true,
        });
        return data;
      },

      // Registration does not sign the user in — the account needs email
      // verification first (see pages/auth/VerifyEmail.jsx).
      async register(payload) {
        return apiClient.post(AUTH.REGISTER, payload);
      },

      async logout(options = {}) {
        const { silent = false } = options;
        const { refreshToken } = get();
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });

        if (!silent && refreshToken) {
          try {
            await apiClient.post(AUTH.LOGOUT, { refresh: refreshToken });
          } catch {
            // Best-effort server-side revocation — local state is already cleared.
          }
        }
      },

      async refreshAccessToken() {
        if (refreshPromise) return refreshPromise;

        const { refreshToken } = get();
        if (!refreshToken) return null;

        refreshPromise = (async () => {
          try {
            const data = await apiClient.post(AUTH.TOKEN_REFRESH, { refresh: refreshToken });
            set({ accessToken: data.access, refreshToken: data.refresh ?? refreshToken });
            return data.access;
          } catch {
            set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
            return null;
          } finally {
            refreshPromise = null;
          }
        })();

        return refreshPromise;
      },

      async fetchCurrentUser() {
        const data = await apiClient.get(AUTH.ME);
        set({ user: data, isAuthenticated: true });
        return data;
      },

      /** Called once on app boot (App.jsx). Rebuilds the session from the
       * persisted refresh token, if there is one. */
      async hydrate() {
        set({ isHydrating: true });
        const { refreshToken } = get();

        if (!refreshToken) {
          set({ isHydrating: false });
          return;
        }

        const accessToken = await get().refreshAccessToken();
        if (accessToken) {
          try {
            await get().fetchCurrentUser();
          } catch {
            set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
          }
        }

        set({ isHydrating: false });
      },
    }),
    {
      name: "provenway-auth",
      storage: createJSONStorage(() => sessionStorage),
      // Only the refresh token is persisted — see the module comment above.
      partialize: (state) => ({ refreshToken: state.refreshToken }),
    }
  )
);

export default useAuthStore;
