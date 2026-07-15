/**
 * src/pages/Landing.jsx
 * ───────────────────────
 * Public marketing landing page. Matches Landing_page design
 * ("Architectural Precision" theme — see DESIGN.md / tokens.css).
 *
 * Static/marketing content only — no backend calls. All CTAs route to
 * /register or /login via React Router. Already-authenticated users are
 * bounced straight to /feed, unless ?preview=1 is present (QA/design checks).
 */
import { Navigate, Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  Camera,
  ClipboardCheck,
  LayoutGrid,
  ShieldCheck,
  TrendingUp,
  Users,
  ExternalLink,
} from "lucide-react";
import Button from "../components/ui/Button";
import LinkButton from "../components/ui/LinkButton";
import ComingSoonCard from "../components/profile/ComingSoonCard";
import PublicNav from "../components/marketing/PublicNav";
import PublicFooter from "../components/marketing/PublicFooter";
import { useAuth } from "../hooks/useAuth";
import { apiClient } from "../lib/api/apiClient";
import { USERS } from "../lib/api/endpoints";
import styles from "./Landing.module.css";

const STEPS = [
  {
    icon: Camera,
    step: "01",
    title: "Document",
    body: "Capture photos, daily logs, and technical specs directly from the site using our mobile-optimised platform.",
  },
  {
    icon: ClipboardCheck,
    step: "02",
    title: "Verify",
    body: "Our verification layer cross-references site location, timestamps, and professional stamps to certify every log.",
  },
  {
    icon: LayoutGrid,
    step: "03",
    title: "Showcase",
    body: "Publish a stunning, secure portfolio that proves your capabilities to future clients and top-tier firms.",
  },
];

const BENEFITS = [
  {
    icon: ShieldCheck,
    title: "Immutable Verification",
    body: "Every log carries GPS and timestamp metadata, making your portfolio difficult to dispute.",
  },
  {
    icon: TrendingUp,
    title: "Career Acceleration",
    body: "Top firms prioritise candidates who can show exactly how they solved problems on-site with real documentation.",
  },
  {
    icon: Users,
    title: "Firm-Wide Transparency",
    body: "Manage entire project teams and consolidate documentation into a single, high-fidelity source of truth for clients.",
  },
];

export default function Landing() {
  const { isAuthenticated, isHydrating } = useAuth();
  const [searchParams] = useSearchParams();
  const isPreview = searchParams.get("preview") === "1";

  // Live count, not a marketing round-number — GET /users/ is public and
  // paginated, so `count` on a 1-result page is a real total at zero cost.
  const { data: verifiedData } = useQuery({
    queryKey: ["landing-verified-count"],
    queryFn: () => apiClient.get(`${USERS.SEARCH}?verified=true&page_size=1`),
    staleTime: 1000 * 60 * 5,
    retry: 1,
  });
  const verifiedCount = verifiedData?.count ?? 0;

  // Already-signed-in users don't need the marketing page, unless they're
  // previewing it on purpose (QA/design checks) via ?preview=1.
  if (!isHydrating && isAuthenticated && !isPreview) {
    return <Navigate to="/feed" replace />;
  }

  return (
    <div className={styles.page}>
      <PublicNav />

      {/* ── Hero ────────────────────────────────────────────────────── */}
      <section className={styles.hero}>
        <div className={styles.heroInner}>
          <div>
            <span className={styles.eyebrow}>Verified Proof of Work</span>
            <h1 className={styles.heroHeadline}>
              Show What
              <br />
              <span className={styles.heroHeadlineAccent}>You&apos;ve Built.</span>
            </h1>
            <p className={styles.heroSubtext}>
              Provenway helps construction professionals create verified proof-of-work portfolios
              through real project documentation. Turn every job site into a career asset.
            </p>
            <div className={styles.heroActions}>
              <LinkButton
                to={isAuthenticated ? "/feed" : "/register"}
                variant="accent"
                size="lg"
                className={styles.heroPrimaryBtn}
              >
                Create Your Build Log <ArrowRight size={18} />
              </LinkButton>
              <LinkButton to="/register" variant="secondary" size="lg">
                Explore Projects
              </LinkButton>
            </div>
            {verifiedCount > 0 && (
              <div className={styles.heroSocial}>
                <p className={styles.heroSocialText}>
                  <strong>{verifiedCount.toLocaleString()}</strong> Verified Professionals
                  documenting
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* ── How it works ────────────────────────────────────────────── */}
      <section className={styles.section}>
        <div className={styles.sectionInner}>
          <div className={styles.sectionHead}>
            <h2 className={styles.sectionTitle}>Building Your Reputation</h2>
            <p className={styles.sectionSubtitle}>
              A seamless three-step process to transform your daily work into a professional,
              verifiable legacy.
            </p>
          </div>
          <div className={styles.stepsGrid}>
            {STEPS.map(({ icon: Icon, step, title, body }) => (
              <div key={step} className={styles.stepCard}>
                <div className={styles.stepIconWrap}>
                  <Icon size={28} />
                  <span className={styles.stepNumber}>{step}</span>
                </div>
                <h3 className={styles.stepTitle}>{title}</h3>
                <p className={styles.stepBody}>{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Featured projects ───────────────────────────────────────── */}
      <section className={styles.sectionAlt}>
        <div className={styles.sectionInner}>
          <div className={styles.rowHead}>
            <div>
              <h2 className={styles.sectionTitle}>Verified Projects</h2>
              <p className={styles.sectionSubtitleTight}>
                Explore high-fidelity proof-of-work from around the region.
              </p>
            </div>
            <Link to="/search" className={styles.viewAllLink}>
              View All Projects <ExternalLink size={14} />
            </Link>
          </div>

          <ComingSoonCard
            icon={LayoutGrid}
            title="Coming Soon"
            description="Real verified build logs from our professionals will appear here."
          />
        </div>
      </section>

      {/* ── Featured professionals ──────────────────────────────────── */}
      <section className={styles.section}>
        <div className={styles.sectionInner}>
          <div className={styles.sectionHead}>
            <h2 className={styles.sectionTitle}>Elite Professionals</h2>
            <p className={styles.sectionSubtitle}>
              Meet the builders and designers who prove their work every day.
            </p>
          </div>

          <ComingSoonCard
            icon={Users}
            title="Coming Soon"
            description="Verified professionals on Provenway will appear here."
          />
        </div>
      </section>

      {/* ── Benefits ─────────────────────────────────────────────────── */}
      <section id="solutions" className={styles.sectionAlt}>
        <div className={styles.sectionInner}>
          <div className={styles.benefitsGrid}>
            <div>
              <h2 className={styles.sectionTitle}>Why Provenway Matters</h2>
              <div className={styles.benefitsList}>
                {BENEFITS.map(({ icon: Icon, title, body }) => (
                  <div key={title} className={styles.benefitRow}>
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
          </div>
        </div>
      </section>

      {/* ── Final CTA ────────────────────────────────────────────────── */}
      <section className={styles.finalCtaSection}>
        <div className={styles.finalCtaCard}>
          <div className={styles.finalCtaPattern} aria-hidden="true" />
          <div className={styles.finalCtaContent}>
            <h2 className={styles.finalCtaTitle}>Ready to Prove Your Expertise?</h2>
            <p className={styles.finalCtaSubtitle}>
              Join the next generation of construction professionals building a legacy through
              verified data.
            </p>
            <div className={styles.finalCtaActions}>
              <LinkButton to="/register" variant="accent" size="lg">
                Start Your First Log
              </LinkButton>
              <Button variant="ghost" size="lg" className={styles.finalCtaGhostBtn}>
                Schedule a Demo
              </Button>
            </div>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
}
