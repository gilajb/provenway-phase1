/**
 * src/pages/auth/ForgotPassword.jsx
 * ────────────────────────────────────
 * Requests a password-reset email. Always shows the same success
 * message regardless of whether the email exists on an account — no
 * user enumeration (Engineering Doc §6.1 threat model).
 */
import { useState } from "react";
import { AlertCircle, ArrowLeft, MailCheck } from "lucide-react";
import { Link } from "react-router-dom";

import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import LinkButton from "../../components/ui/LinkButton";
import { apiClient } from "../../lib/api/apiClient";
import { AUTH } from "../../lib/api/endpoints";
import { getErrorMessage } from "../../lib/api/errorMessages";
import { validateEmail } from "../../utils/validation";
import styles from "./Auth.module.css";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [fieldError, setFieldError] = useState(null);
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError(null);
    const error = validateEmail(email);
    setFieldError(error);
    if (error) return;

    setLoading(true);
    try {
      await apiClient.post(AUTH.PASSWORD_RESET_REQUEST, { email: email.trim() });
      setSent(true);
    } catch (err) {
      setFormError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  if (sent) {
    return (
      <div className={styles.successState}>
        <div className={styles.successIcon}>
          <MailCheck size={26} />
        </div>
        <h1 className={styles.successTitle}>Check your email</h1>
        <p className={styles.successText}>
          If an account exists for <strong>{email.trim()}</strong>, you&apos;ll receive a
          password reset link shortly.
        </p>
        <div className={styles.successActions}>
          <LinkButton to="/login" variant="secondary" fullWidth>
            Back to sign in
          </LinkButton>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className={styles.header}>
        <h1 className={styles.title}>Reset your password</h1>
        <p className={styles.subtitle}>Enter your email and we&apos;ll send you a reset link.</p>
      </div>

      {formError && (
        <div className={styles.errorBanner} role="alert">
          <AlertCircle size={16} />
          <span>{formError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.form} noValidate>
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          value={email}
          error={fieldError}
          onChange={(e) => {
            setEmail(e.target.value);
            if (fieldError) setFieldError(null);
          }}
        />
        <Button type="submit" fullWidth loading={loading}>
          Send reset link
        </Button>
      </form>

      <Link to="/login" className={styles.backLink}>
        <ArrowLeft size={14} /> Back to sign in
      </Link>
    </>
  );
}
