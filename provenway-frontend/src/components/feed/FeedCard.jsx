/**
 * src/components/feed/FeedCard.jsx
 * ─────────────────────────────────
 * One ProjectUpdate in the home feed, rendered as a large standalone
 * card (16px corner radius — DESIGN.md's "Large Layout Containers"
 * rule) rather than the compact timeline row UpdateEntry.jsx uses on
 * the project page. UpdateEntry is built as a timeline <li> with a
 * connecting-line marker, which doesn't fit a feed of independent
 * cards from many authors/projects — so this component is new, but it
 * deliberately reuses UpdateEntry's already-solved pieces rather than
 * re-implementing them: Badge for the entry-type pill, PhotoGrid
 * as-is for photos, entryTypeLabel/formatDate/timeAgo, and the same
 * "body is server-sanitised, safe to render as HTML" note (Engineering
 * Doc §3.2.3 / §6.1 — bleach whitelist on the server).
 *
 * Field-name note (same defensive approach as ProfessionalCard.jsx /
 * ProjectPage.jsx): the exact nesting the feed serializer uses for the
 * author and parent-project info wasn't available while building this,
 * so field access falls back across a couple of likely shapes. Update
 * the getters below if the real serializer differs.
 */
import { Link } from "react-router-dom";
import { CalendarDays, FolderKanban, MapPin } from "lucide-react";

import Avatar from "../ui/Avatar";
import Badge from "../ui/Badge";
import VerifiedBadge from "../profile/VerifiedBadge";
import PhotoGrid from "../project/PhotoGrid";
import { entryTypeLabel } from "../../utils/projectEnums";
import { formatDate, timeAgo } from "../../utils/dates";

import styles from "./FeedCard.module.css";

function getAuthor(update) {
  return update?.author ?? update?.user ?? update?.created_by ?? {};
}

function getProject(update) {
  return update?.project ?? update?.parent_project ?? {};
}

export default function FeedCard({ update }) {
  const author = getAuthor(update);
  const project = getProject(update);

  const authorId = author?.id ?? author?.user_id;
  const authorName = author?.display_name ?? "Provenway Professional";
  const authorHeadline = author?.headline ?? null;
  const isVerified = Boolean(author?.is_verified);

  const projectId = project?.id;
  const projectTitle = project?.title;

  const hasGeotag = Boolean(update?.geotag_lat || update?.geotag_lng);

  return (
    <article className={styles.card}>
      <header className={styles.header}>
        <Link to={authorId ? `/profile/${authorId}` : "#"} className={styles.avatarLink}>
          <Avatar src={author?.avatar_url} name={authorName} size={48} />
        </Link>

        <div className={styles.authorMeta}>
          <Link to={authorId ? `/profile/${authorId}` : "#"} className={styles.authorName}>
            {authorName}
          </Link>
          {isVerified && <VerifiedBadge size={10} />}

          <p className={styles.subline}>
            {authorHeadline && <span>{authorHeadline}</span>}
            {authorHeadline && update?.created_at && <span aria-hidden="true"> • </span>}
            {update?.created_at && <span>{timeAgo(update.created_at)}</span>}
          </p>
        </div>
      </header>

      {projectTitle && (
        <Link to={projectId ? `/projects/${projectId}` : "#"} className={styles.projectChip}>
          <FolderKanban size={13} />
          {projectTitle}
        </Link>
      )}

      <div className={styles.badgeRow}>
        {update?.entry_type && <Badge variant="primary">{entryTypeLabel(update.entry_type)}</Badge>}
        {hasGeotag && (
          <span className={styles.geotag}>
            <MapPin size={12} />
            Geotagged
          </span>
        )}
      </div>

      {update?.title && <p className={styles.title}>{update.title}</p>}
      {update?.body && (
        // Server-sanitised rich text (bleach whitelist) — same rendering
        // approach as UpdateEntry.jsx, safe to render as HTML.
        <div className={styles.body} dangerouslySetInnerHTML={{ __html: update.body }} />
      )}

      <PhotoGrid photos={update?.photos} />

      <footer className={styles.footer}>
        {update?.entry_date && (
          <span className={styles.dateBadge}>
            <CalendarDays size={12} />
            {formatDate(update.entry_date)}
          </span>
        )}

        {projectId && (
          <Link to={`/projects/${projectId}`} className={styles.viewLink}>
            View project
          </Link>
        )}
      </footer>
    </article>
  );
}
