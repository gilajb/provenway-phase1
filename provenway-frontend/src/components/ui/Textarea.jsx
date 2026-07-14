/**
 * src/components/ui/Textarea.jsx
 * ────────────────────────────────
 * Labelled multi-line text input. Reuses Input.module.css so it looks
 * identical to <Input> (same border, focus glow, label, hint, error
 * treatment) rather than duplicating those styles.
 */
import { forwardRef, useId } from "react";
import { clsx } from "clsx";
import styles from "./Input.module.css";

const Textarea = forwardRef(function Textarea(
  { label, hint, error, rows = 4, maxLength, className, value = "", ...props },
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
      <textarea
        id={id}
        ref={ref}
        rows={rows}
        maxLength={maxLength}
        value={value}
        className={clsx(styles.input, error && styles.hasError, className)}
        style={{ height: "auto", padding: "10px var(--space-sm)", resize: "vertical" }}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        aria-invalid={!!error}
        {...props}
      />
      {maxLength && (
        <p className={styles.hint} style={{ textAlign: "right" }}>
          {value.length}/{maxLength}
        </p>
      )}
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

export default Textarea;
