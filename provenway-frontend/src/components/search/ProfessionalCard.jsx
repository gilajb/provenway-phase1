/**
 * src/components/search/ProfessionalCard.jsx
 * ─────────────────────────────────────────────
 * A single result card in the directory search grid. Links to the
 * professional's profile page.
 *
 * Field-name note (same defensive approach as ProfilePage.jsx): the exact
 * shape of a GET /users/ result row wasn't available while building this,
 * so field access falls back across a couple of likely shapes. Update the
 * getters below if the real serializer differs.
 */
import { Link } from "react-router-dom";
import { MapPin } from "lucide-react";

import Avatar from "../ui/Avatar";
import VerifiedBadge from "../profile/VerifiedBadge";
import DisciplineTags from "../profile/DisciplineTags";

import styles from "./ProfessionalCard.module.css";

function getDisplayName(person) {
  return person?.display_name ?? person?.user?.display_name ?? "Provenway Professional";
}

function getHeadline(person) {
  return person?.headline ?? person?.user?.headline ?? null;
}

function getIsVerified(person) {
  return Boolean(person?.is_verified ?? person?.user?.is_verified);
}

export default function ProfessionalCard({ person }) {
  const id = person?.id ?? person?.user_id ?? person?.user?.id;
  const displayName = getDisplayName(person);
  const headline = getHeadline(person);
  const isVerified = getIsVerified(person);
  const disciplines = person?.disciplines ?? [];
  const location = person?.location_text ?? null;

  return (
    <Link to={`/profile/${id}`} className={styles.card}>
      <div className={styles.topRow}>
        <div className={styles.avatarWrap}>
          <Avatar src={person?.avatar_url} name={displayName} size={56} />
          {isVerified && (
            <span className={styles.verifiedDot} aria-hidden="true">
              <VerifiedBadgeDot />
            </span>
          )}
        </div>
      </div>

      <h3 className={styles.name}>{displayName}</h3>
      {headline && <p className={styles.headline}>{headline}</p>}

      {isVerified && (
        <div className={styles.badgeRow}>
          <VerifiedBadge />
        </div>
      )}

      {disciplines.length > 0 && (
        <div className={styles.disciplines}>
          <DisciplineTags disciplines={disciplines} max={3} />
        </div>
      )}

      {location && (
        <div className={styles.footer}>
          <MapPin size={14} />
          <span>{location}</span>
        </div>
      )}
    </Link>
  );
}

// Small teal check mark badge overlaid on the avatar corner, in addition to
// the full "Verified" pill below the name — mirrors the design reference's
// avatar-corner verified glyph while reusing Badge's teal token colours.
function VerifiedBadgeDot() {
  return (
    <span className={styles.dotInner}>
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M20 6L9 17l-5-5"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </span>
  );
}
