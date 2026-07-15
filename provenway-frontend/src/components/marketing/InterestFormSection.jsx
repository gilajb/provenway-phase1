/**
 * src/components/marketing/InterestFormSection.jsx
 * ─────────────────────────────────────────────────
 * Wraps InterestForm in the page section that "For Construction Firms"
 * and "Educational Access" scroll their hero CTA to (#interest-form).
 * Pulled out as its own component since both pages need the identical
 * wrapper, not just the bare form.
 */
import InterestForm from "./InterestForm";
import styles from "./InterestFormSection.module.css";

export default function InterestFormSection({ title, subtitle, interestType, sourcePage }) {
  return (
    <section id="interest-form" className={styles.section}>
      <div className={styles.sectionInner}>
        <div className={styles.card}>
          <div className={styles.cardText}>
            <h2 className={styles.title}>{title}</h2>
            {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
          </div>
          <div className={styles.formWrap}>
            <InterestForm interestType={interestType} sourcePage={sourcePage} />
          </div>
        </div>
      </div>
    </section>
  );
}
