/**
 * src/pages/auth/ResetPassword.jsx
 * ───────────────────────────────────
 * Confirms a password reset using the token from the emailed link
 * (?token=...). All existing sessions are revoked server-side on
 * success, so the user has to sign in again afterward.
 */
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { AlertCircle, CheckCircle2, XCircle } from "lucide-react";

import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import LinkButton from "../../components/ui/LinkButton";
import PasswordStrengthMeter from "../../components/ui/PasswordStrengthMeter";
import { apiClient } from "../../lib/api/apiClient";
import { AUTH } from "../../lib/api/endpoints";
import { getErrorMessage } from "../../lib/api/errorMessages";
import { validatePassword, validateConfirmPassword } from "../../utils/validation";
import styles from "./Auth.module.css";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [form, setForm] = useState({ password: "", confirmPassword: "" });
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  function updateField(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
    if (fieldErrors[field]) setFieldErrors((f) => ({ ...f, [field]: null }));
  }

  function validate() {
    const errors = {
      password: validatePassword(form.password),
      confirmPassword: validateConfirmPassword(form.password, form.confirmPassword),
    };
    setFieldErrors(errors);
    return !Object.values(errors).some(Boolean);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError(null);
    if (!validate()) return;

    setLoading(true);
    try {
      await apiClient.post(AUTH.PASSWORD_RESET_CONFIRM, {
        token,
        new_password: form.password,
      });
      setDone(true);
    } catch (err) {
      setFormError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className={styles.successState}>
        <div className={styles.errorIcon}>
          <XCircle size={26} />
        </div>
        <h1 className={styles.successTitle}>Invalid reset link</h1>
        <p className={styles.successText}>
          This password reset link is missing or malformed. Request a new one to continue.
        </p>
        <div className={styles.successActions}>
          <LinkButton to="/forgot-password" fullWidth>
            Request a new link
          </LinkButton>
        </div>
      </div>
    );
  }

  if (done) {
    return (
      <div className={styles.successState}>
        <div className={styles.successIcon}>
          <CheckCircle2 size={26} />
        </div>
        <h1 className={styles.successTitle}>Password reset</h1>
        <p className={styles.successText}>
          Your password has been updated. Please sign in again with your new password.
        </p>
        <div className={styles.successActions}>
          <LinkButton to="/login" fullWidth>
            Go to sign in
          </LinkButton>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className={styles.header}>
        <h1 className={styles.title}>Set a new password</h1>
        <p className={styles.subtitle}>Choose a new password for your account.</p>
      </div>

      {formError && (
        <div className={styles.errorBanner} role="alert">
          <AlertCircle size={16} />
          <span>{formError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.form} noValidate>
        <div>
          <Input
            label="New password"
            type="password"
            autoComplete="new-password"
            value={form.password}
            error={fieldErrors.password}
            hint={!fieldErrors.password ? "Min 8 characters, 1 uppercase letter, 1 number." : undefined}
            onChange={(e) => updateField("password", e.target.value)}
          />
          <PasswordStrengthMeter password={form.password} />
        </div>

        <Input
          label="Confirm new password"
          type="password"
          autoComplete="new-password"
          value={form.confirmPassword}
          error={fieldErrors.confirmPassword}
          onChange={(e) => updateField("confirmPassword", e.target.value)}
        />

        <Button type="submit" fullWidth loading={loading}>
          Reset password
        </Button>
      </form>
    </>
  );
}
