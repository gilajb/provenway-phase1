/**
 * src/components/profile/ComingSoonCard.jsx
 * ─────────────────────────────────────────────
 * Placeholder for design sections that don't have a backing API yet
 * (build log, career timeline, achievements, project portfolio — all
 * still stub apps per the build plan). Styled per DESIGN.md's blueprint
 * grid treatment for "no image present" states, so the page reads as
 * intentionally-not-built-yet rather than broken or hiding real data.
 */
import styles from "./ComingSoonCard.module.css";

export default function ComingSoonCard({ icon: Icon, title, description }) {
  return (
    <div className={styles.card}>
      <div className={styles.blueprint} aria-hidden="true" />
      <div className={styles.content}>
        {Icon && <Icon size={22} className={styles.icon} />}
        <p className={styles.title}>{title}</p>
        {description && <p className={styles.description}>{description}</p>}
      </div>
    </div>
  );
}
