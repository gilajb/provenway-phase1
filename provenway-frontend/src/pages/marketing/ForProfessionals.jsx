/**
 * src/pages/marketing/ForProfessionals.jsx
 * ───────────────────────────────────────────
 * Broad, discipline-agnostic Solutions page covering every individual
 * persona in Engineering Doc §1.3 (architect, civil/structural engineer,
 * QS, contractor, site supervisor, PM, interior designer, MEP engineer).
 * Same live signup CTA as Landing's hero — /register today exists and
 * genuinely does what this page describes.
 */
import { Camera, ShieldCheck, TrendingUp } from "lucide-react";
import AudiencePageLayout from "../../components/marketing/AudiencePageLayout";
import { useAuth } from "../../hooks/useAuth";

const VALUE_PROPS = [
  {
    icon: Camera,
    title: "Document as You Work",
    body: "Log dated updates with photos, site notes, and technical specs directly from your phone — no separate portfolio to maintain later.",
  },
  {
    icon: ShieldCheck,
    title: "Verified, Not Just Claimed",
    body: "Every entry carries a server timestamp that can't be backdated, so your build log is evidence, not just a resume line.",
  },
  {
    icon: TrendingUp,
    title: "A Portfolio That Follows Your Career",
    body: "One profile across every project and every employer — build a track record that's yours, not locked in a firm's old files.",
  },
];

export default function ForProfessionals() {
  const { isAuthenticated } = useAuth();

  return (
    <AudiencePageLayout
      eyebrow="For Individual Professionals"
      headline="Your Work,"
      headlineAccent="Documented and Verified."
      subtext="Whatever your discipline — architecture, civil or structural engineering, quantity surveying, contracting, site supervision, project management, interior design, or MEP — Provenway turns your daily work into a proof-of-work portfolio you actually own."
      primaryCta={{ label: isAuthenticated ? "Go to Your Feed" : "Create Your Free Account", to: isAuthenticated ? "/feed" : "/register" }}
      secondaryCta={{ label: "Sign In", to: "/login" }}
      valuePropsTitle="Built for How You Already Work"
      valueProps={VALUE_PROPS}
      finalCta={{
        title: "Start Your Build Log Today",
        subtitle: "Free to join. Your first update takes less than five minutes to log.",
        primary: { label: "Create Your Free Account", to: "/register" },
      }}
    />
  );
}
