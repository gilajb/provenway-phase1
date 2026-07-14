/**
 * src/pages/auth/Register.jsx
 * ─────────────────────────────
 * Registration form. On success, shows an email-verification prompt —
 * the account exists immediately, but verifying the email is what
 * eventually unlocks the verified badge (Engineering Doc §1.4.7).
 */
import { useState } from "react";
import { AlertCircle, MailCheck } from "lucide-react";

import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import LinkButton from "../../components/ui/LinkButton";
import PasswordStrengthMeter from "../../components/ui/PasswordStrengthMeter";
import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { getErrorMessage, getFieldErrors } from "../../lib/api/errorMessages";
import {
  validateEmail,
  validatePassword,
  validateConfirmPassword,
  validateRequired,
  validatePhone,
} from "../../utils/validation";
import styles from "./Auth.module.css";

const INITIAL_FORM = { display_name: "", email: "", phone: "", password: "", confirmPassword: "" };

export default function Register() {
  const { register } = useAuth();
  const [form, setForm] = useState(INITIAL_FORM);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submittedEmail, setSubmittedEmail] = useState(null);

  function updateField(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
    if (fieldErrors[field]) setFieldErrors((f) => ({ ...f, [field]: null }));
  }

  function validate() {
    const errors = {
      display_name: validateRequired(form.display_name, "Full name"),
      email: validateEmail(form.email),
      phone: validatePhone(form.phone),
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
      const payload = {
        display_name: form.display_name.trim(),
        email: form.email.trim(),
        password: form.password,
      };
      if (form.phone.trim()) payload.phone = form.phone.trim();

      await register(payload);
      setSubmittedEmail(form.email.trim());
    } catch (err) {
      setFieldErrors((f) => ({ ...f, ...getFieldErrors(err) }));
      setFormError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  if (submittedEmail) {
    return (
      <div className={styles.successState}>
        <div className={styles.successIcon}>
          <MailCheck size={26} />
        </div>
        <h1 className={styles.successTitle}>Check your email</h1>
        <p className={styles.successText}>
          We sent a verification link to <strong>{submittedEmail}</strong>. Click it to
          verify your account.
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
        <h1 className={styles.title}>Create your account</h1>
        <p className={styles.subtitle}>Start building your verified proof-of-work portfolio.</p>
      </div>

      {formError && (
        <div className={styles.errorBanner} role="alert">
          <AlertCircle size={16} />
          <span>{formError}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className={styles.form} noValidate>
        <Input
          label="Full name"
          autoComplete="name"
          value={form.display_name}
          error={fieldErrors.display_name}
          onChange={(e) => updateField("display_name", e.target.value)}
        />

        <Input
          label="Email"
          type="email"
          autoComplete="email"
          value={form.email}
          error={fieldErrors.email}
          onChange={(e) => updateField("email", e.target.value)}
        />

        <Input
          label="Phone (optional)"
          type="tel"
          autoComplete="tel"
          placeholder="+254 7XX XXX XXX"
          value={form.phone}
          error={fieldErrors.phone}
          onChange={(e) => updateField("phone", e.target.value)}
        />

        <div>
          <Input
            label="Password"
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
          label="Confirm password"
          type="password"
          autoComplete="new-password"
          value={form.confirmPassword}
          error={fieldErrors.confirmPassword}
          onChange={(e) => updateField("confirmPassword", e.target.value)}
        />

        <Button type="submit" fullWidth loading={loading}>
          Create account
        </Button>
      </form>

      <p className={styles.linksRow}>
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </>
  );
}
