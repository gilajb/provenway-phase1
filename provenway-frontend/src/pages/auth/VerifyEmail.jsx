/**
 * src/pages/auth/VerifyEmail.jsx
 * ─────────────────────────────────
 * Confirms the token from the emailed verification link (?token=...)
 * against POST /auth/verify-email/. Runs automatically on mount — this
 * page has no form, only status states.
 */
import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";

import LinkButton from "../../components/ui/LinkButton";
import { apiClient } from "../../lib/api/apiClient";
import { AUTH } from "../../lib/api/endpoints";
import { getErrorMessage } from "../../lib/api/errorMessages";
import styles from "./Auth.module.css";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [status, setStatus] = useState(token ? "verifying" : "missing");
  const [message, setMessage] = useState(null);
  const attempted = useRef(false);

  useEffect(() => {
    if (!token || attempted.current) return;
    attempted.current = true;

    (async () => {
      try {
        await apiClient.post(AUTH.VERIFY_EMAIL, { token });
        setStatus("success");
      } catch (err) {
        setStatus("error");
        setMessage(getErrorMessage(err));
      }
    })();
  }, [token]);

  if (status === "verifying") {
    return (
      <div className={styles.centerState}>
        <Loader2 size={26} className={styles.spinnerIcon} />
        <p className={styles.successText}>Verifying your email…</p>
      </div>
    );
  }

  if (status === "success") {
    return (
      <div className={styles.successState}>
        <div className={styles.successIcon}>
          <CheckCircle2 size={26} />
        </div>
        <h1 className={styles.successTitle}>Email verified</h1>
        <p className={styles.successText}>Your email is confirmed. You can now sign in.</p>
        <div className={styles.successActions}>
          <LinkButton to="/login" fullWidth>
            Go to sign in
          </LinkButton>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className={styles.successState}>
        <div className={styles.errorIcon}>
          <XCircle size={26} />
        </div>
        <h1 className={styles.successTitle}>Verification failed</h1>
        <p className={styles.successText}>
          {message ?? "This verification link is invalid or has expired."}
        </p>
        <div className={styles.successActions}>
          <LinkButton to="/login" variant="secondary" fullWidth>
            Back to sign in
          </LinkButton>
        </div>
      </div>
    );
  }

  // status === "missing" — page opened without a token in the URL
  return (
    <div className={styles.successState}>
      <h1 className={styles.successTitle}>Check your email</h1>
      <p className={styles.successText}>
        We sent a verification link to your inbox when you registered. Open it on this
        device to verify your account.
      </p>
      <div className={styles.successActions}>
        <LinkButton to="/login" variant="secondary" fullWidth>
          Back to sign in
        </LinkButton>
      </div>
    </div>
  );
}
