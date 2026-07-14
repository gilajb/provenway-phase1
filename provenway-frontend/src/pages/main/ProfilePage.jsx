/**
 * src/pages/main/ProfilePage.jsx
 * ──────────────────────────────
 * Public + own profile view, backed by apps/profiles
 * (GET/PATCH /profiles/me/, GET /profiles/{user_id}/, avatar upload).
 *
 * NOTE on scope: the Portfolio/Profile design (screen.png) also shows a
 * career-journey timeline, achievements, portfolio projects, and live
 * build logs with follower/following counts. None of that has a backing
 * API yet (build_log, networking, and verification are still stub apps
 * per the build plan) — so rather than inventing numbers or fake history,
 * those sections render as clearly-labelled "coming soon" placeholders
 * styled to the design system. Everything else (avatar, name, headline,
 * verified badge, bio, disciplines, location, years of experience, firm)
 * is wired to real data and fully editable for the profile owner.
 *
 * Also flagging a field-name assumption for review: the exact response
 * shape of GET /profiles/{user_id}/ wasn't available while building this,
 * so field access below is defensive (falls back across a couple of
 * likely shapes — e.g. flat `display_name` vs nested `user.display_name`).
 * Update getDisplayName/getHeadline/getIsVerified below if the real
 * serializer differs.
 */
import { useState } from "react";
import { useParams } from "react-router-dom";
import {
  MapPin,
  Building2,
  Pencil,
  Hammer,
  Layers,
  History,
  AlertCircle,
} from "lucide-react";

import { useProfile } from "../../hooks/useProfile";
import { useAuth } from "../../hooks/useAuth";
import { getErrorMessage } from "../../lib/api/errorMessages";

import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import VerifiedBadge from "../../components/profile/VerifiedBadge";
import DisciplineTags from "../../components/profile/DisciplineTags";
import AvatarUpload from "../../components/profile/AvatarUpload";
import EditProfileModal from "../../components/profile/EditProfileModal";
import ComingSoonCard from "../../components/profile/ComingSoonCard";

import styles from "./ProfilePage.module.css";

function getDisplayName(data) {
  return data?.display_name ?? data?.user?.display_name ?? "Provenway Professional";
}

function getHeadline(data) {
  return data?.headline ?? data?.user?.headline ?? null;
}

function getIsVerified(data) {
  return Boolean(data?.is_verified ?? data?.user?.is_verified);
}

export default function ProfilePage() {
  const { id } = useParams();
  const { user: currentUser } = useAuth();
  const { data, isLoading, isError, error, updateProfile, uploadAvatar } = useProfile(id);
  const [isEditOpen, setIsEditOpen] = useState(false);

  if (isLoading) {
    return <ProfileSkeleton />;
  }

  if (isError) {
    return (
      <div className={styles.errorState} role="alert">
        <AlertCircle size={20} />
        <p>{getErrorMessage(error)}</p>
      </div>
    );
  }

  if (!data) return null;

  const isOwnProfile = data.is_own_profile ?? currentUser?.id === id;
  const displayName = getDisplayName(data);
  const headline = getHeadline(data);
  const isVerified = getIsVerified(data);
  const disciplines = data.disciplines ?? [];

  return (
    <div className={styles.page}>
      <div className={styles.grid}>
        {/* ── Left column: identity card ─────────────────────────────── */}
        <aside className={styles.sidebar}>
          <div className={styles.card}>
            <AvatarUpload
              src={data.avatar_url}
              name={displayName}
              size={120}
              editable={isOwnProfile}
              uploadAvatar={uploadAvatar}
            />

            <h1 className={styles.name}>{displayName}</h1>
            {headline && <p className={styles.headline}>{headline}</p>}
            {isVerified && (
              <div className={styles.verifiedRow}>
                <VerifiedBadge />
              </div>
            )}

            {isOwnProfile && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setIsEditOpen(true)}
                className={styles.editButton}
              >
                <span className={styles.buttonContent}>
                  <Pencil size={14} />
                  Edit profile
                </span>
              </Button>
            )}

            <div className={styles.metaList}>
              {data.location_text && (
                <div className={styles.metaRow}>
                  <MapPin size={16} />
                  <span>{data.location_text}</span>
                </div>
              )}
              {data.firm_name && (
                <div className={styles.metaRow}>
                  <Building2 size={16} />
                  <span>{data.firm_name}</span>
                </div>
              )}
              {(data.years_of_experience || data.years_of_experience === 0) && (
                <div className={styles.metaRow}>
                  <Badge variant="muted">
                    {data.years_of_experience}{" "}
                    {data.years_of_experience === 1 ? "year" : "years"} experience
                  </Badge>
                </div>
              )}
            </div>

            {disciplines.length > 0 && (
              <div className={styles.section}>
                <p className={styles.sectionLabel}>Specialty</p>
                <DisciplineTags disciplines={disciplines} />
              </div>
            )}
          </div>
        </aside>

        {/* ── Right column: bio + placeholders ───────────────────────── */}
        <main className={styles.main}>
          <section className={styles.card}>
            <p className={styles.sectionLabel}>About</p>
            {data.bio ? (
              <p className={styles.bio}>{data.bio}</p>
            ) : (
              <p className={styles.emptyBio}>
                {isOwnProfile
                  ? "You haven't written a bio yet. Add one so other professionals know your story."
                  : "This professional hasn't added a bio yet."}
              </p>
            )}
          </section>

          <section className={styles.comingSoonGrid}>
            <ComingSoonCard
              icon={Hammer}
              title="Build Log"
              description="Dated, photographic site updates are coming soon."
            />
            <ComingSoonCard
              icon={Layers}
              title="Portfolio Projects"
              description="Completed and active projects will appear here."
            />
            <ComingSoonCard
              icon={History}
              title="Professional Journey"
              description="Career timeline and achievements are coming soon."
            />
          </section>
        </main>
      </div>

      {isOwnProfile && (
        <EditProfileModal
          isOpen={isEditOpen}
          onClose={() => setIsEditOpen(false)}
          profile={data}
          updateProfile={updateProfile}
        />
      )}
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div className={styles.page}>
      <div className={styles.grid}>
        <aside className={styles.sidebar}>
          <div className={`${styles.card} ${styles.skeletonCard}`}>
            <div className={`${styles.skeleton} ${styles.skeletonAvatar}`} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "60%" }} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "40%" }} />
          </div>
        </aside>
        <main className={styles.main}>
          <div className={`${styles.card} ${styles.skeletonCard}`}>
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "30%" }} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "90%" }} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "80%" }} />
          </div>
        </main>
      </div>
    </div>
  );
}
