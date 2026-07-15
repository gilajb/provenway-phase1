/**
 * src/components/marketing/AudiencePageLayout.jsx
 * ───────────────────────────────────────────────────
 * Shared shape for the 4 "Solutions" audience pages (For Professionals,
 * For Architects, For Construction Firms, Educational Access): nav ->
 * hero -> value props -> optional page-specific middle section
 * (children) -> final CTA -> footer. Mirrors Landing.jsx's own
 * hero/section/benefits/final-CTA visual pattern so all 5 public pages
 * read as one system, without forcing Landing itself (a richer, already
 * bespoke page) into this shape.
 *
 * `primaryCta`/`secondaryCta` accept either `{ label, to }` (an
 * in-app route, rendered as a router Link) or `{ label, href }` (a
 * plain anchor — used for the "#interest-form" scroll target on the
 * Firms/Educational pages, which don't have a live signup route to
 * link to).
 */
import { Link } from "react-router-dom";
import { clsx } from "clsx";
import LinkButton from "../ui/LinkButton";
import btnStyles from "../ui/Button.module.css";
import PublicNav from "./PublicNav";
import PublicFooter from "./PublicFooter";
import styles from "./AudiencePageLayout.module.css";

function CtaLink({ cta, variant, size = "lg", className }) {
  if (!cta) return null;
  if (cta.to) {
    return (
      <LinkButton to={cta.to} variant={variant} size={size} className={className}>
        {cta.label}
      </LinkButton>
    );
  }
  return (
    <a
      href={cta.href}
      className={clsx(btnStyles.btn, btnStyles[variant], btnStyles[size], className)}
    >
      {cta.label}
    </a>
  );
}

export default function AudiencePageLayout({
  eyebrow,
  headline,
  headlineAccent,
  subtext,
  primaryCta,
  secondaryCta,
  valuePropsTitle = "Why It Matters",
  valueProps = [],
  children,
  finalCta,
}) {
  return (
    <div className={styles.page}>
      <PublicNav />

      {/* ── Hero ────────────────────────────────────────────────────── */}
      <section className={styles.hero}>
        <div className={styles.heroInner}>
          {eyebrow && <span className={styles.eyebrow}>{eyebrow}</span>}
          <h1 className={styles.heroHeadline}>
            {headline}
            {headlineAccent && (
              <>
                <br />
                <span className={styles.heroHeadlineAccent}>{headlineAccent}</span>
              </>
            )}
          </h1>
          {subtext && <p className={styles.heroSubtext}>{subtext}</p>}
          <div className={styles.heroActions}>
            <CtaLink cta={primaryCta} variant="accent" className={styles.heroPrimaryBtn} />
            <CtaLink cta={secondaryCta} variant="secondary" />
          </div>
        </div>
      </section>

      {/* ── Value props ─────────────────────────────────────────────── */}
      {valueProps.length > 0 && (
        <section className={styles.section}>
          <div className={styles.sectionInner}>
            <div className={styles.sectionHead}>
              <h2 className={styles.sectionTitle}>{valuePropsTitle}</h2>
            </div>
            <div className={styles.valuePropsGrid}>
              {valueProps.map(({ icon: Icon, title, body }) => (
                <div key={title} className={styles.valuePropCard}>
                  <div className={styles.benefitIconWrap}>
                    <Icon size={22} />
                  </div>
                  <div>
                    <h4 className={styles.benefitTitle}>{title}</h4>
                    <p className={styles.benefitBody}>{body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {children}

      {/* ── Final CTA ────────────────────────────────────────────────── */}
      {finalCta && (
        <section className={styles.finalCtaSection}>
          <div className={styles.finalCtaCard}>
            <div className={styles.finalCtaPattern} aria-hidden="true" />
            <div className={styles.finalCtaContent}>
              <h2 className={styles.finalCtaTitle}>{finalCta.title}</h2>
              <p className={styles.finalCtaSubtitle}>{finalCta.subtitle}</p>
              <div className={styles.finalCtaActions}>
                <CtaLink cta={finalCta.primary} variant="accent" />
                {finalCta.secondaryLabel && (
                  <Link to="/" className={clsx(btnStyles.btn, btnStyles.ghost, btnStyles.lg, styles.finalCtaGhostBtn)}>
                    {finalCta.secondaryLabel}
                  </Link>
                )}
              </div>
            </div>
          </div>
        </section>
      )}

      <PublicFooter />
    </div>
  );
}
