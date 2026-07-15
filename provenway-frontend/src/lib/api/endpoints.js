/**
 * src/lib/api/endpoints.js
 * ────────────────────────
 * Central registry of all API endpoint paths.
 * Import from here rather than hard-coding paths in hooks.
 */

export const AUTH = {
  REGISTER:               "/auth/register/",
  VERIFY_EMAIL:           "/auth/verify-email/",
  LOGIN:                  "/auth/login/",
  TOKEN_REFRESH:          "/auth/token/refresh/",
  LOGOUT:                 "/auth/logout/",
  PASSWORD_RESET_REQUEST: "/auth/password-reset/request/",
  PASSWORD_RESET_CONFIRM: "/auth/password-reset/confirm/",
  OTP_REQUEST:            "/auth/otp/request/",
  OTP_VERIFY:             "/auth/otp/verify/",
  // MeView lives on the authentication app and is live today. USERS.ME
  // below (/users/me/) is the Engineering-Doc-spec'd path but apps/profiles
  // isn't mounted in urls.py yet — use this one until that ships.
  ME:                     "/auth/me/",
};

export const USERS = {
  ME:          "/users/me/",
  ANALYTICS:   "/users/me/analytics/",
  DATA_EXPORT: "/users/me/data-export/",
  by_id:       (id) => `/users/${id}/`,
  SEARCH:      "/users/",
  follow:      (id) => `/users/${id}/follow/`,
  followers:   (id) => `/users/${id}/followers/`,
  following:   (id) => `/users/${id}/following/`,
  block:       (id) => `/users/${id}/block/`,
};

// apps/profiles/ — live today. Profile is the single source of truth for
// bio, location, avatar_url, and disciplines. GET by_id() works for any
// profile (returns is_own_profile); PATCH and avatar upload only ever
// target /me/.
export const PROFILES = {
  ME:     "/profiles/me/",
  AVATAR: "/profiles/me/avatar/",
  by_id:  (userId) => `/profiles/${userId}/`,
};

export const CREDENTIALS = {
  LIST:    "/credentials/",
  ME:      "/credentials/me/",
};

export const PROJECTS = {
  LIST:           "/projects/",
  by_id:          (id) => `/projects/${id}/`,
  UPDATES:        (id) => `/projects/${id}/updates/`,
  update:         (id, uid) => `/projects/${id}/updates/${uid}/`,
  photos:         (id, uid) => `/projects/${id}/updates/${uid}/photos/`,
  cosign:         (id, uid) => `/projects/${id}/updates/${uid}/cosign/`,
  cosign_confirm: (id, uid) => `/projects/${id}/updates/${uid}/cosign/confirm/`,
  export_pdf:     (id) => `/projects/${id}/export-pdf/`,
};

export const FEED = {
  HOME:      "/feed/",
  DISCOVER:  "/feed/discover/",
  TRENDING:  "/feed/trending/",
};

export const JOBS = {
  LIST:         "/jobs/",
  by_id:        (id) => `/jobs/${id}/`,
  apply:        (id) => `/jobs/${id}/apply/`,
  applications: (id) => `/jobs/${id}/applications/`,
  application:  (id, aid) => `/jobs/${id}/applications/${aid}/`,
};

export const TENDERS = {
  LIST:    "/tenders/",
  by_id:   (id) => `/tenders/${id}/`,
  bid:     (id) => `/tenders/${id}/bid/`,
  bids:    (id) => `/tenders/${id}/bids/`,
  award:   (id) => `/tenders/${id}/award/`,
};

export const CONVERSATIONS = {
  LIST:     "/conversations/",
  messages: (id) => `/conversations/${id}/messages/`,
};

export const MESSAGES = {
  by_id: (id) => `/messages/${id}/`,
};

export const NOTIFICATIONS = {
  LIST:        "/notifications/",
  read:        (id) => `/notifications/${id}/read/`,
  READ_ALL:    "/notifications/read-all/",
  PREFERENCES: "/notifications/preferences/",
};

export const TASKS = {
  by_id: (taskId) => `/tasks/${taskId}/`,
};

export const SEARCH = {
  ALL: "/search/",
};

// apps/leads — public lead capture for marketing pages whose product
// area (firms, institutions) has no self-serve account flow yet.
export const LEADS = {
  INTEREST: "/leads/interest/",
};

export const WEBSOCKET = {
  chat:          (conversationId) =>
    `${import.meta.env.VITE_API_URL?.replace("http", "ws")?.replace("/api/v1", "")}/ws/chat/${conversationId}/`,
  notifications: () =>
    `${import.meta.env.VITE_API_URL?.replace("http", "ws")?.replace("/api/v1", "")}/ws/notifications/`,
};
