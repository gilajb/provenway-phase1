/**
 * src/lib/api/apiClient.js
 * ────────────────────────
 * Axios instance for all Provenway API calls.
 *
 * - Base URL from VITE_API_URL (falls back to local dev backend)
 * - Request interceptor attaches the in-memory JWT access token
 * - Response interceptor silently refreshes the access token on a 401
 *   (using the refresh token held in the auth store), retries the
 *   original request once, and signs the user out + redirects to
 *   /login if the refresh also fails
 * - Errors are normalised into ApiError (status + RFC 7807 body) so
 *   every caller reads err.status / err.body.detail / err.body.errors
 *   the same way no matter what failed
 *
 * apiClient.get/post/patch/put/delete resolve directly to the parsed
 * response body (not the full axios response) — this preserves the
 * call-site contract already used across the app (useProfile.js,
 * useFeed.js, useNotifications.js, etc).
 */
import axios from "axios";
import { useAuthStore } from "../../stores/authStore";
import { AUTH } from "./endpoints";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(status, body) {
    super(body?.detail ?? body?.title ?? `Request failed (${status})`);
    this.name = "ApiError";
    this.status = status;
    this.body = body ?? {};
  }
}

const http = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json", Accept: "application/json" },
});

// These must never trigger a refresh-and-retry cycle on 401 — refreshing
// off a failed login/register, or off the refresh call itself, would loop.
const NO_RETRY_PATHS = [AUTH.LOGIN, AUTH.REGISTER, AUTH.TOKEN_REFRESH, AUTH.LOGOUT];

http.interceptors.request.use((config) => {
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Shared in-flight refresh promise so concurrent 401s trigger one refresh,
// not one per failed request.
let refreshPromise = null;

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;

    if (!response) {
      // Network error, timeout, CORS failure, etc — no HTTP response at all.
      return Promise.reject(
        new ApiError(0, { detail: "Can't reach the server. Check your connection and try again." })
      );
    }

    const isNoRetryPath = config && NO_RETRY_PATHS.some((path) => config.url?.startsWith(path));

    if (response.status === 401 && config && !config._retried && !isNoRetryPath) {
      config._retried = true;
      try {
        if (!refreshPromise) {
          refreshPromise = useAuthStore.getState().refreshAccessToken();
        }
        const newAccessToken = await refreshPromise;
        refreshPromise = null;

        if (newAccessToken) {
          config.headers = config.headers ?? {};
          config.headers.Authorization = `Bearer ${newAccessToken}`;
          return http(config);
        }
      } catch {
        refreshPromise = null;
      }

      // Refresh failed (or there was no refresh token) — the session is
      // over. Clear state locally (silent: skip the network logout call,
      // it would just 401 again) and send the user back to /login.
      useAuthStore.getState().logout({ silent: true });
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }

    return Promise.reject(new ApiError(response.status, response.data));
  }
);

export const apiClient = {
  get: (path, config) => http.get(path, config).then((r) => r.data),
  post: (path, body, config) => http.post(path, body, config).then((r) => r.data),
  patch: (path, body, config) => http.patch(path, body, config).then((r) => r.data),
  put: (path, body, config) => http.put(path, body, config).then((r) => r.data),
  delete: (path, config) => http.delete(path, config).then((r) => r.data),
};

export default apiClient;
export { http as axiosInstance };
