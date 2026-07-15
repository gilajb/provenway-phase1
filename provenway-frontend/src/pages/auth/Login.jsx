/**
 * src/pages/auth/Login.jsx
 * ─────────────────────────
 * Email + password sign-in. Redirects to the page the user was headed
 * to (via ProtectedRoute's redirect state) or /feed on success.
 */
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AlertCircle } from "lucide-react";

import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import { useAuth } from "../../hooks/useAuth";
import { getErrorMessage, getFieldErrors } from "../../lib/api/errorMessages";
import { validateEmail, validateRequired } from "../../utils/validation";
import styles from "./Auth.module.css";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname ?? "/feed";

  const [form, setForm] = useState({ email: "", password: "" });
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);

  function updateField(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
    if (fieldErrors[field]) setFieldErrors((f) => ({ ...f, [field]: null }));
  }

  function validate() {
    const errors = {
      email: validateEmail(form.email),
      password: validateRequired(form.password, "Password"),
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
      await login(form.email.trim(), form.password);
      navigate(from, { replace: true });
    } catch (err) {
      setFieldErrors((f) => ({ ...f, ...getFieldErrors(err) }));
      setFormError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className={styles.header}>
        <h1 className={styles.title}>Sign in</h1>
        <p className={styles.subtitle}>Welcome back to Provenway.</p>
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
          value={form.email}
          error={fieldErrors.email}
          onChange={(e) => updateField("email", e.target.value)}
        />

        <div>
          <Input
            label="Password"
            type="password"
            autoComplete="current-password"
            value={form.password}
            error={fieldErrors.password}
            onChange={(e) => updateField("password", e.target.value)}
          />
          <div className={styles.forgotRow}>
            <Link to="/forgot-password" className={styles.forgotLink}>
              Forgot password?
            </Link>
          </div>
        </div>

        <Button type="submit" fullWidth loading={loading}>
          Sign in
        </Button>
      </form>

      <p className={styles.linksRow}>
        Don&apos;t have an account? <Link to="/register">Create one</Link>
      </p>
    </>
  );
}
