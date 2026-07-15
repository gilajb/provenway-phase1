/**
 * src/pages/marketing/EducationalAccess.jsx
 * ─────────────────────────────────────────────
 * apps.verification is an empty backend stub — there's no bulk
 * graduate-verification workflow to offer yet (Engineering Doc
 * §1.4.7 "Institution partnerships"). This page is pitched entirely
 * as an expression of interest for that future partnership, not a
 * working feature, and its CTA routes to InterestFormSection rather
 * than a signup flow that doesn't exist for institutions.
 */
import { ShieldCheck, TrendingUp, Users } from "lucide-react";
import AudiencePageLayout from "../../components/marketing/AudiencePageLayout";
import InterestFormSection from "../../components/marketing/InterestFormSection";

const VALUE_PROPS = [
  {
    icon: ShieldCheck,
    title: "Bulk Graduate Verification",
    body: "Confirm your graduates' credentials at scale, giving them an instant, institution-backed trust signal the moment they enter the job market. In development.",
  },
  {
    icon: TrendingUp,
    title: "A Head Start on Their Careers",
    body: "Graduates who join Provenway can start building a verified proof-of-work portfolio from their very first project — no cold-start CV required.",
  },
  {
    icon: Users,
    title: "Partner With Provenway",
    body: "We're looking for founding university and professional-body partners to help shape how bulk verification works. Register your interest to start the conversation.",
  },
];

export default function EducationalAccess() {
  return (
    <AudiencePageLayout
      eyebrow="Educational Access"
      headline="Give Your Graduates a"
      headlineAccent="Verified Head Start."
      subtext="We're building institution partnerships for bulk graduate and member verification — a direct, credible trust signal that follows your graduates from graduation into their first job search. This is early-stage: register your interest and help shape it."
      primaryCta={{ label: "Register Your Institution's Interest", href: "#interest-form" }}
      valuePropsTitle="What We're Building"
      valueProps={VALUE_PROPS}
    >
      <InterestFormSection
        title="Partner With Us"
        subtitle="Tell us about your institution and we'll be in touch as this program takes shape."
        interestType="educational_institution"
        sourcePage="educational-access"
      />
    </AudiencePageLayout>
  );
}
