/**
 * src/pages/marketing/ForArchitects.jsx
 * ────────────────────────────────────────
 * Architect is one persona among several individual professional types
 * (Engineering Doc §1.3) with identical live functionality to
 * ForProfessionals.jsx — there's no feature gap to point to. This page
 * reuses the same layout and CTA (live /register), differentiated only
 * through architecture-specific copy and one added middle section.
 */
import { Award, Camera, FileText, MapPin, PenTool, ShieldCheck } from "lucide-react";
import AudiencePageLayout from "../../components/marketing/AudiencePageLayout";
import { useAuth } from "../../hooks/useAuth";
import styles from "./ForArchitects.module.css";

const VALUE_PROPS = [
  {
    icon: PenTool,
    title: "From Concept to Completion",
    body: "Log design iterations, drawing revisions, and site-supervision visits in one continuous, dated record — not scattered across email threads and old hard drives.",
  },
  {
    icon: ShieldCheck,
    title: "Verified, Not Just Claimed",
    body: "Every entry carries a server timestamp that can't be backdated, so your portfolio shows real, verifiable involvement in every project.",
  },
  {
    icon: Camera,
    title: "A Portfolio Clients Can Trust",
    body: "Share a live build log instead of a static PDF — prospective clients see the process, not just the finished renders.",
  },
];

const DOCUMENT_STAGES = [
  { icon: PenTool, label: "Concept Sketches" },
  { icon: FileText, label: "Construction Drawings" },
  { icon: MapPin, label: "Site Walkthroughs" },
  { icon: Award, label: "Completion Certificates" },
];

export default function ForArchitects() {
  const { isAuthenticated } = useAuth();

  return (
    <AudiencePageLayout
      eyebrow="For Architects"
      headline="Your Designs,"
      headlineAccent="From Sketch to Site."
      subtext="Provenway gives architects a single, verified record of a project's full lifecycle — concept sketches, drawing revisions, client presentations, and site-supervision walkthroughs — built from the work you're already doing."
      primaryCta={{ label: isAuthenticated ? "Go to Your Feed" : "Create Your Free Account", to: isAuthenticated ? "/feed" : "/register" }}
      secondaryCta={{ label: "Sign In", to: "/login" }}
      valuePropsTitle="Built for the Architectural Process"
      valueProps={VALUE_PROPS}
      finalCta={{
        title: "Start Documenting Your Next Project",
        subtitle: "Free to join. Your first update takes less than five minutes to log.",
        primary: { label: "Create Your Free Account", to: "/register" },
      }}
    >
      <section className={styles.stagesSection}>
        <div className={styles.stagesInner}>
          <h2 className={styles.stagesTitle}>What Architects Document on Provenway</h2>
          <div className={styles.stagesGrid}>
            {DOCUMENT_STAGES.map(({ icon: Icon, label }, i) => (
              <div key={label} className={styles.stageCard}>
                <div className={styles.stageIconWrap}>
                  <Icon size={22} />
                </div>
                <span className={styles.stageLabel}>{label}</span>
                {i < DOCUMENT_STAGES.length - 1 && <span className={styles.stageArrow} aria-hidden="true">→</span>}
              </div>
            ))}
          </div>
        </div>
      </section>
    </AudiencePageLayout>
  );
}
