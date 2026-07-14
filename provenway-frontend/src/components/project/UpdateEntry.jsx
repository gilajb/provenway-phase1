/**
 * src/components/project/UpdateEntry.jsx
 * ──────────────────────────────────────────
 * One item in the build-log timeline. Restyled (Build Log Experience
 * design, this session) to match the reference's "Update History" rows:
 * a solid primary-blue marker with a soft halo, a compact primary-
 * coloured title, and a right-aligned date pill on a surface-container
 * background — rather than each entry living inside its own bordered
 * card. There's no "upcoming/hollow circle" state here — every
 * ProjectUpdate that exists has already happened, unlike the mockup's
 * planned-milestone items.
 */
import { CalendarDays, MapPin } from "lucide-react";
import Badge from "../ui/Badge";
import PhotoGrid from "./PhotoGrid";
import { entryTypeLabel } from "../../utils/projectEnums";
import { formatDate, timeAgo } from "../../utils/dates";
import styles from "./UpdateEntry.module.css";

export default function UpdateEntry({ update }) {
  return (
    <li className={styles.item}>
      <span className={styles.marker} aria-hidden="true" />
      <div className={styles.row}>
        <div className={styles.content}>
          <div className={styles.badgeRow}>
            <Badge variant="primary">{entryTypeLabel(update.entry_type)}</Badge>
            {(update.geotag_lat || update.geotag_lng) && (
              <span className={styles.geotag}>
                <MapPin size={12} />
                Geotagged
              </span>
            )}
          </div>

          {update.title && <p className={styles.title}>{update.title}</p>}
          {update.body && (
            // body is server-side sanitised (bleach whitelist — Engineering
            // Doc §3.2.3 / §6.1) rich text, so it's safe to render as HTML
            // rather than escaping it into literal tag text.
            <div className={styles.body} dangerouslySetInnerHTML={{ __html: update.body }} />
          )}

          <PhotoGrid photos={update.photos} />

          {update.created_at && (
            <p className={styles.posted}>Posted {timeAgo(update.created_at)}</p>
          )}
        </div>

        <span className={styles.dateBadge}>
          <CalendarDays size={12} />
          {formatDate(update.entry_date)}
        </span>
      </div>
    </li>
  );
}
