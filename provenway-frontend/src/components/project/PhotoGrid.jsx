/**
 * src/components/project/PhotoGrid.jsx
 * ────────────────────────────────────────
 * Renders an UpdatePhoto[] array for a single update, always in
 * sequence_order (0–9, unique per update — Engineering Doc §3.2.3),
 * never in raw API response order.
 */
import { useState } from "react";
import styles from "./PhotoGrid.module.css";

export default function PhotoGrid({ photos = [] }) {
  const [expanded, setExpanded] = useState(null);

  if (photos.length === 0) return null;

  const ordered = [...photos].sort(
    (a, b) => (a.sequence_order ?? 0) - (b.sequence_order ?? 0)
  );

  return (
    <>
      <div className={styles.grid} data-count={Math.min(ordered.length, 5)}>
        {ordered.slice(0, 4).map((photo, i) => (
          <button
            key={photo.id ?? `${photo.url}-${i}`}
            type="button"
            className={styles.tile}
            onClick={() => setExpanded(photo)}
            aria-label="View photo full size"
          >
            <img src={photo.url} alt="" loading="lazy" />
            {i === 3 && ordered.length > 4 && (
              <span className={styles.overflow}>+{ordered.length - 4}</span>
            )}
          </button>
        ))}
      </div>

      {expanded && (
        <div
          className={styles.lightbox}
          onMouseDown={(e) => e.target === e.currentTarget && setExpanded(null)}
        >
          <img src={expanded.url} alt="" />
        </div>
      )}
    </>
  );
}
