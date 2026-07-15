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
import {
  ArrowRight,
  Camera,
  ClipboardCheck,
  LayoutGrid,
  ShieldCheck,
  TrendingUp,
  Users,
  MapPin,
  FileText,
  Star,
  CheckCircle2,
  ExternalLink,
  Globe,
  Share2,
} from "lucide-react";
import Button from "../components/ui/Button";
import LinkButton from "../components/ui/LinkButton";
import { useAuth } from "../hooks/useAuth";
import styles from "./Landing.module.css";

const NAV_LINKS = ["Explore", "Solutions", "Firms", "Pricing"];

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

const PROFESSIONALS = [
  { name: "Marcus Thorne", role: "Lead Architect, Structura", tags: ["STEEL", "CAD", "PM"] },
  { name: "Elena Rodriguez", role: "Senior PM, Vanguard Group", tags: ["SITE OPS", "BIM", "SAFETY"] },
  { name: "David Chen", role: "Structural Engineer", tags: ["CONCRETE", "SEISMIC"] },
  { name: "Sarah Jenkins", role: "Interior Designer, ARC-WEST", tags: ["FINISHES", "LIGHTING", "3D"] },
];

const TESTIMONIALS = [
  {
    quote:
      "Provenway has changed the way I interview. Instead of just talking about my experience, I can show a verified history of every major project I've touched.",
    name: "Robert Hall",
    role: "Senior Site Superintendent",
  },
  {
    quote:
      "For our firm, Provenway is the gold standard for quality control. We can monitor progress across 20 sites in real time with verified visual data.",
    name: "Linda Zhao",
    role: "Director of Operations, ARC-WEST",
  },
  {
    quote:
      "The transparency this platform provides to our clients is unmatched. It builds trust from day one of the construction phase.",
    name: "Jameson Burke",
    role: "Lead Project Architect",
  },
];

const FOOTER_COLUMNS = [
  {
    heading: "Product",
    links: ["Build Logs", "Verification Hub", "Portfolio Designer", "Integrations"],
  },
  {
    heading: "Solutions",
    links: ["For Professionals", "For Construction Firms", "For Architects", "Educational Access"],
  },
  {
    heading: "Company",
    links: ["About Us", "Careers", "Verification Standards", "Contact"],
  },
  {
    heading: "Resources",
    links: ["Case Studies", "Industry Reports", "Blog", "Support Center"],
  },
];

const TRUST_LOGOS = ["STRUCTURA", "ARC-WEST", "BUILD-PRO", "MERIDIAN", "VANGUARD"];

export default function Landing() {
  const { isAuthenticated, isHydrating } = useAuth();
  const [searchParams] = useSearchParams();
  const isPreview = searchParams.get("preview") === "1";

  // Already-signed-in users don't need the marketing page, unless they're
  // previewing it on purpose (QA/design checks) via ?preview=1.
  if (!isHydrating && isAuthenticated && !isPreview) {
    return <Navigate to="/feed" replace />;
  }

  return (
    <div className={styles.page}>
      {/* ── Nav ─────────────────────────────────────────────────────── */}
      <nav className={styles.nav}>
        <div className={styles.navInner}>
          <div className={styles.navLeft}>
            <span className={styles.brand}>Provenway</span>
            <div className={styles.navLinks}>
              {NAV_LINKS.map((label, i) => (
                <a key={label} href="#" className={i === 0 ? styles.navLinkActive : styles.navLink}>
                  {label}
                </a>
              ))}
            </div>
          </div>
          <div className={styles.navRight}>
            <Link to="/login" className={styles.signInLink}>
              Sign In
            </Link>
            <LinkButton to="/register" variant="primary" size="md">
              Sign Up
            </LinkButton>
          </div>
        </div>
      </nav>

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
              <LinkButton to="/register" variant="accent" size="lg" className={styles.heroPrimaryBtn}>
                Create Your Build Log <ArrowRight size={18} />
              </LinkButton>
              <LinkButton to="/register" variant="secondary" size="lg">
                Explore Projects
              </LinkButton>
            </div>
            <div className={styles.heroSocial}>
              <div className={styles.avatarStack}>
                <span className={styles.stackAvatar} />
                <span className={styles.stackAvatar} />
                <span className={styles.stackAvatar} />
              </div>
              <p className={styles.heroSocialText}>
                <strong>2,500+</strong> Verified Professionals documenting
              </p>
            </div>
          </div>

          <div className={styles.heroCardWrap}>
            <div className={styles.heroCard}>
              <div className={styles.heroCardImage} aria-hidden="true" />
              <div className={styles.heroCardBody}>
                <div className={styles.heroCardHead}>
                  <div>
                    <h3 className={styles.heroCardTitle}>Skyline Residence Phase 1</h3>
                    <p className={styles.heroCardMeta}>Nairobi, KE • Project ID: PW-9921</p>
                  </div>
                  <span className={styles.verifiedPill}>
                    <CheckCircle2 size={12} /> Verified
                  </span>
                </div>
                <div className={styles.heroCardFooter}>
                  <FileText size={16} /> 14 Documentation Logs
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Social proof ────────────────────────────────────────────── */}
      <section className={styles.trustStrip}>
        <div className={styles.sectionInner}>
          <p className={styles.trustLabel}>Trusted by industry leaders</p>
          <div className={styles.trustLogos}>
            {TRUST_LOGOS.map((logo) => (
              <span key={logo} className={styles.trustLogo}>
                {logo}
              </span>
            ))}
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
            <button type="button" className={styles.viewAllLink}>
              View All Projects <ExternalLink size={14} />
            </button>
          </div>

          <div className={styles.bentoGrid}>
            <div className={styles.bentoMain}>
              <div className={styles.bentoPattern} aria-hidden="true" />
              <div className={styles.bentoOverlay} />
              <div className={styles.bentoContent}>
                <div className={styles.bentoMeta}>
                  <span className={styles.verifiedPillDark}>Verified Log</span>
                  <span className={styles.bentoDate}>June 2026</span>
                </div>
                <h3 className={styles.bentoTitle}>The Nexus Tech Plaza</h3>
                <p className={styles.bentoBody}>
                  Advanced structural steel installation and smart glass integration. Documented
                  through 42 verified build logs.
                </p>
              </div>
            </div>
            <div className={styles.bentoSide}>
              <div className={styles.bentoSmall}>
                <div className={styles.bentoPattern} aria-hidden="true" />
                <div className={styles.bentoOverlay} />
                <div className={styles.bentoSmallContent}>
                  <h4 className={styles.bentoSmallTitle}>Oak Valley Lofts</h4>
                  <p className={styles.bentoSmallMeta}>Interior Masterwork • Karen, Nairobi</p>
                </div>
              </div>
              <div className={styles.bentoSmall}>
                <div className={styles.bentoPattern} aria-hidden="true" />
                <div className={styles.bentoOverlay} />
                <div className={styles.bentoSmallContent}>
                  <h4 className={styles.bentoSmallTitle}>Eco-Campus Courtyard</h4>
                  <p className={styles.bentoSmallMeta}>Sustainable Design • Kiambu</p>
                </div>
              </div>
            </div>
          </div>
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
          <div className={styles.proGrid}>
            {PROFESSIONALS.map((pro) => (
              <div key={pro.name} className={styles.proCard}>
                <div className={styles.proAvatarWrap}>
                  <div className={styles.proAvatar} />
                  <span className={styles.proVerifiedDot}>
                    <CheckCircle2 size={14} />
                  </span>
                </div>
                <h3 className={styles.proName}>{pro.name}</h3>
                <p className={styles.proRole}>{pro.role}</p>
                <div className={styles.proTags}>
                  {pro.tags.map((tag) => (
                    <span key={tag} className={styles.proTag}>
                      {tag}
                    </span>
                  ))}
                </div>
                <Link to="/register" className={styles.proBtn}>
                  View Portfolio
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Benefits ─────────────────────────────────────────────────── */}
      <section className={styles.sectionAlt}>
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

            <div className={styles.mockupFrame}>
              <div className={styles.mockupInner}>
                <div className={styles.mockupHead}>
                  <div className={styles.mockupHeadLeft}>
                    <div className={styles.mockupLogo}>PW</div>
                    <div>
                      <p className={styles.mockupTitle}>Build Log #442</p>
                      <p className={styles.mockupSubtitle}>Foundation Pouring • 10:42 AM</p>
                    </div>
                  </div>
                  <span className={styles.mockupLocation}>
                    <MapPin size={12} /> Verified Location
                  </span>
                </div>
                <div className={styles.mockupPattern} aria-hidden="true" />
                <div className={styles.mockupLines}>
                  <span className={styles.mockupLine} style={{ width: "100%" }} />
                  <span className={styles.mockupLine} style={{ width: "75%" }} />
                  <span className={styles.mockupLine} style={{ width: "50%" }} />
                </div>
                <div className={styles.mockupFooter}>
                  <span className={styles.mockupApprove}>Approve Log</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Testimonials ────────────────────────────────────────────── */}
      <section className={styles.section}>
        <div className={styles.sectionInner}>
          <h2 className={styles.sectionTitleCenter}>Heard from the Site</h2>
          <div className={styles.testimonialGrid}>
            {TESTIMONIALS.map((t) => (
              <div key={t.name} className={styles.testimonialCard}>
                <div className={styles.stars}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} size={16} fill="currentColor" strokeWidth={0} />
                  ))}
                </div>
                <p className={styles.testimonialQuote}>&ldquo;{t.quote}&rdquo;</p>
                <div className={styles.testimonialAuthor}>
                  <div className={styles.testimonialAvatar} />
                  <div>
                    <p className={styles.testimonialName}>{t.name}</p>
                    <p className={styles.testimonialRole}>{t.role}</p>
                  </div>
                </div>
              </div>
            ))}
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

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer className={styles.footer}>
        <div className={styles.sectionInner}>
          <div className={styles.footerGrid}>
            <div className={styles.footerBrandCol}>
              <span className={styles.footerBrand}>Provenway</span>
              <p className={styles.footerTagline}>
                The construction industry&apos;s standard for verified documentation and
                professional portfolios.
              </p>
              <div className={styles.footerSocial}>
                <a href="#" className={styles.footerSocialIcon} aria-label="Website">
                  <Globe size={16} />
                </a>
                <a href="#" className={styles.footerSocialIcon} aria-label="Share">
                  <Share2 size={16} />
                </a>
              </div>
            </div>

            {FOOTER_COLUMNS.map((col) => (
              <div key={col.heading}>
                <h5 className={styles.footerHeading}>{col.heading}</h5>
                <ul className={styles.footerLinks}>
                  {col.links.map((link) => (
                    <li key={link}>
                      <a href="#" className={styles.footerLink}>
                        {link}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className={styles.footerBottom}>
            <p className={styles.footerCopyright}>© 2026 Provenway. All rights reserved.</p>
            <div className={styles.footerLegal}>
              <a href="#" className={styles.footerLegalLink}>
                Privacy Policy
              </a>
              <a href="#" className={styles.footerLegalLink}>
                Terms of Service
              </a>
              <a href="#" className={styles.footerLegalLink}>
                Trust &amp; Security
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
