/**
 * src/components/ui/Select.jsx
 * ─────────────────────────────
 * Labelled <select>. Reuses Input.module.css so it looks identical to
 * <Input>/<Textarea> (same border, focus glow, label, error treatment)
 * — no existing select component was found in src/components/ui/.
 */
import { forwardRef, useId } from "react";
import { clsx } from "clsx";
import styles from "./Input.module.css";

const Select = forwardRef(function Select(
  { label, hint, error, options = [], className, ...props },
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
      <select
        id={id}
        ref={ref}
        className={clsx(styles.input, error && styles.hasError, className)}
        aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
        aria-invalid={!!error}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
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

export default Select;
