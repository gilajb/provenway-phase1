/**
 * src/components/layout/AuthLayout.jsx
 * ─────────────────────────────────────
 * Wrapper for unauthenticated pages (login, register, reset-password).
 * Centred single-column layout with Provenway branding.
 */
import { Outlet } from "react-router-dom";
import styles from "./AuthLayout.module.css";

export default function AuthLayout() {
  return (
    <div className={styles.root}>
      <div className={styles.card}>
        <div className={styles.brand}>
          <span className={styles.brandName}>Provenway</span>
          <p className={styles.brandTagline}>Your proof-of-work, on the record.</p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
