/**
 * src/components/ui/Badge.jsx
 * ────────────────────────────
 * Pill-shaped badge. Variants: default | success (verified) | primary | muted.
 */

import { clsx } from "clsx";
import styles from "./Badge.module.css";

export default function Badge({ children, variant = "default", className }) {
  return (
    <span className={clsx(styles.badge, styles[variant], className)}>
      {children}
    </span>
  );
}
