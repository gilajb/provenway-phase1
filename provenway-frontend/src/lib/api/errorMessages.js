/**
 * src/lib/api/errorMessages.js
 * ─────────────────────────────
 * Maps ApiError (see apiClient.js) to copy a person can actually read.
 * The backend follows RFC 7807 (Engineering Doc §5.1): error bodies have
 * `detail` (human string) and sometimes `errors` (field -> message[]).
 */

const STATUS_FALLBACKS = {
  0: "Can't reach the server. Check your connection and try again.",
  400: "Please check the highlighted fields and try again.",
  401: "That email and password combination doesn't match our records.",
  403: "You don't have permission to do that.",
  404: "We couldn't find what you were looking for.",
  409: "That already exists.",
  429: "Too many attempts. Please wait a moment and try again.",
  500: "Something went wrong on our end. Please try again shortly.",
  502: "The server is temporarily unavailable. Please try again shortly.",
  503: "The server is temporarily unavailable. Please try again shortly.",
};

/** Top-level, form-banner-friendly message for an ApiError. */
export function getErrorMessage(err) {
  if (!err) return "Something went wrong. Please try again.";

  const detail = err.body?.detail;
  if (typeof detail === "string" && detail.trim()) return detail;

  return STATUS_FALLBACKS[err.status] ?? "Something went wrong. Please try again.";
}

/**
 * Extracts per-field messages from a DRF-style `errors` object so they
 * can be merged into a form's field-error state, e.g.:
 *   { email: ["user with this email already exists."] } -> { email: "user with this email already exists." }
 */
export function getFieldErrors(err) {
  const errors = err?.body?.errors;
  if (!errors || typeof errors !== "object") return {};

  const fieldErrors = {};
  for (const [field, messages] of Object.entries(errors)) {
    fieldErrors[field] = Array.isArray(messages) ? messages[0] : String(messages);
  }
  return fieldErrors;
}
