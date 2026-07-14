/**
 * src/components/ui/Input.jsx
 * ────────────────────────────
 * Labelled text input with error state, hint text, and focus glow.
 */

import { forwardRef, useId } from "react";
import { clsx } from "clsx";
import styles from "./Input.module.css";

const Input = forwardRef(function Input(
  { label, hint, error, type = "text", className, ...props },
  ref
) {
  const id = useId();

  return (
    <div className={styles.wrapper}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label}
        </label>
      )}
      <input
        id={id}
        ref={ref}
        type={type}
        className={clsx(styles.input, error && styles.hasError, className)}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        aria-invalid={!!error}
        {...props}
      />
      {hint && !error && (
        <p id={`${id}-hint`} className={styles.hint}>
          {hint}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className={styles.error} role="alert">
          {error}
        </p>
      )}
    </div>
  );
});

export default Input;
