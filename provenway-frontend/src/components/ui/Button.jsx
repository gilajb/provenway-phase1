/**
 * src/components/ui/Button.jsx
 * ─────────────────────────────
 * Primary design system button.
 * Variants: primary | secondary | accent | ghost | danger
 * Sizes:    sm | md | lg
 */

import { clsx } from "clsx";
import styles from "./Button.module.css";

export default function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  fullWidth = false,
  type = "button",
  onClick,
  className,
  ...props
}) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={clsx(
        styles.btn,
        styles[variant],
        styles[size],
        fullWidth && styles.fullWidth,
        loading && styles.loading,
        className
      )}
      {...props}
    >
      {loading ? <span className={styles.spinner} aria-hidden="true" /> : null}
      <span className={loading ? styles.hiddenText : undefined}>{children}</span>
    </button>
  );
}
