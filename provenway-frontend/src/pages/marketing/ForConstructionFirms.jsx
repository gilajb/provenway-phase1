/**
 * src/pages/marketing/ForConstructionFirms.jsx
 * ────────────────────────────────────────────────
 * apps.organisations/billing/recruitment are empty backend stubs and
 * Register.jsx only ever creates an individual account — there's no
 * self-serve "firm account" to sign up for yet. This page is honest
 * about that: it describes what firms can genuinely do today (browse
 * verified individual profiles and build logs) and frames recruiter
 * seats / job & tender postings as roadmap, with the primary CTA
 * routed to InterestFormSection instead of /register.
 */
import { Camera, ShieldCheck, Users } from "lucide-react";
import AudiencePageLayout from "../../components/marketing/AudiencePageLayout";
import InterestFormSection from "../../components/marketing/InterestFormSection";

const VALUE_PROPS = [
  {
    icon: ShieldCheck,
    title: "Browse Verified Profiles Today",
    body: "Search the Provenway directory by discipline, location, and verified status — available now, no waitlist.",
  },
  {
    icon: Camera,
    title: "See Real Work, Not Just a CV",
    body: "Every profile links to a dated build log — photos, site updates, and timestamps you can review before you ever pick up the phone.",
  },
  {
    icon: Users,
    title: "Recruiter Tools — Coming Soon",
    body: "Dedicated firm accounts, job and tender postings, and candidate search are on our roadmap. Register your interest and we'll notify you at launch.",
  },
];

export default function ForConstructionFirms() {
  return (
    <AudiencePageLayout
      eyebrow="For Construction Firms"
      headline="Vet Talent by"
      headlineAccent="What They've Actually Built."
      subtext="Provenway's directory of verified professionals and dated build logs is live today. Firm accounts, job postings, and tender marketplace tools are coming — register your interest to be first in line."
      primaryCta={{ label: "Request Early Access", href: "#interest-form" }}
      valuePropsTitle="What Firms Get"
      valueProps={VALUE_PROPS}
    >
      <InterestFormSection
        title="Get Early Access for Your Firm"
        subtitle="Tell us a bit about your firm and we'll reach out when recruiter and posting tools launch."
        interestType="construction_firm"
        sourcePage="for-construction-firms"
      />
    </AudiencePageLayout>
  );
}
