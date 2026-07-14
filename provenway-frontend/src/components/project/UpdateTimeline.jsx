/**
 * src/components/project/UpdateTimeline.jsx
 * ─────────────────────────────────────────────
 * Vertical-line/circle timeline shell (DESIGN.md "construction schedule"
 * treatment: "Vertical lines (2px, #B4B2A9) with solid primary blue
 * circles for completed steps"). Individual entries render via
 * UpdateEntry; this component owns the connecting line, loading
 * skeleton, empty state, and "load more" pagination.
 */
import { Hammer, AlertCircle } from "lucide-react";
import Button from "../ui/Button";
import UpdateEntry from "./UpdateEntry";
import { getErrorMessage } from "../../lib/api/errorMessages";
import styles from "./UpdateTimeline.module.css";

export default function UpdateTimeline({
  pages,
  isLoading,
  isError,
  error,
  hasNextPage,
  isFetchingNextPage,
  onLoadMore,
  isOwner,
}) {
  if (isLoading) {
    return (
      <ol className={styles.list}>
        <li className={styles.skeletonItem}>
          <div className={styles.skeletonMarker} />
          <div className={styles.skeletonCard} />
        </li>
        <li className={styles.skeletonItem}>
          <div className={styles.skeletonMarker} />
          <div className={styles.skeletonCard} />
        </li>
      </ol>
    );
  }

  if (isError) {
    return (
      <div className={styles.errorState} role="alert">
        <AlertCircle size={18} />
        <span>{getErrorMessage(error)}</span>
      </div>
    );
  }

  const updates = pages?.flatMap((p) => p.results ?? []) ?? [];

  if (updates.length === 0) {
    return (
      <div className={styles.empty}>
        <Hammer size={22} />
        <p>
          {isOwner
            ? "No updates logged yet. Add one to start this project's build log."
            : "No updates have been logged on this project yet."}
        </p>
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      <ol className={styles.list}>
        {updates.map((update) => (
          <UpdateEntry key={update.id} update={update} />
        ))}
      </ol>

      {hasNextPage && (
        <Button
          variant="ghost"
          fullWidth
          onClick={onLoadMore}
          loading={isFetchingNextPage}
          className={styles.loadMore}
        >
          Show previous logs
        </Button>
      )}
    </div>
  );
}
