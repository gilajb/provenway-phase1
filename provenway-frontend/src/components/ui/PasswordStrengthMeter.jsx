/**
 * src/components/ui/PasswordStrengthMeter.jsx
 * ───────────────────────────────────────────
 * Visual strength indicator shown under password fields on
 * Register and ResetPassword. Purely advisory — the backend's
 * validation is still authoritative.
 */
import { passwordStrengthScore } from "../../utils/validation";
import styles from "./PasswordStrengthMeter.module.css";

const LABELS = ["Too weak", "Weak", "Fair", "Good", "Strong"];
const LEVEL_CLASS = ["", styles.level1, styles.level2, styles.level3, styles.level4];

export default function PasswordStrengthMeter({ password }) {
  if (!password) return null;

  const score = passwordStrengthScore(password);

  return (
    <div className={styles.wrapper}>
      <div className={styles.track} aria-hidden="true">
        {[0, 1, 2, 3].map((i) => (
          <span key={i} className={`${styles.segment} ${i < score ? LEVEL_CLASS[score] : ""}`} />
        ))}
      </div>
      <span className={styles.label}>{LABELS[score]}</span>
    </div>
  );
}
