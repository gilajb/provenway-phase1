/**
 * src/utils/validation.js
 * ────────────────────────
 * Shared client-side form validation for the auth flow. Mirrors backend
 * rules (FR-AUTH-04; apps/authentication/serializers.py — min 8 chars,
 * 1 uppercase, 1 number) so people see the same constraints before they
 * ever hit the API. The backend remains the source of truth — its
 * response is still surfaced via getFieldErrors on submit.
 */

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^\+?[0-9\s-]{7,15}$/;

export function validateRequired(value, label = "This field") {
  if (!value || !String(value).trim()) return `${label} is required.`;
  return null;
}

export function validateEmail(value) {
  if (!value || !value.trim()) return "Email is required.";
  if (!EMAIL_RE.test(value.trim())) return "Enter a valid email address.";
  return null;
}

/** Optional field — phone is nullable on the User model. */
export function validatePhone(value) {
  if (!value || !value.trim()) return null;
  if (!PHONE_RE.test(value.trim())) return "Enter a valid phone number.";
  return null;
}

export function validatePassword(value) {
  if (!value) return "Password is required.";
  if (value.length < 8) return "Password must be at least 8 characters.";
  if (!/[A-Z]/.test(value)) return "Password must include at least one uppercase letter.";
  if (!/[0-9]/.test(value)) return "Password must include at least one number.";
  return null;
}

export function validateConfirmPassword(password, confirmation) {
  if (!confirmation) return "Please confirm your password.";
  if (password !== confirmation) return "Passwords don't match.";
  return null;
}

/** 0-4 strength score for the visual meter. Not itself a pass/fail check. */
export function passwordStrengthScore(value) {
  if (!value) return 0;
  let score = 0;
  if (value.length >= 8) score++;
  if (/[A-Z]/.test(value)) score++;
  if (/[0-9]/.test(value)) score++;
  if (/[^A-Za-z0-9]/.test(value) || value.length >= 12) score++;
  return score;
}
