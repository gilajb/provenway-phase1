/**
 * src/pages/main/FeedPage.jsx
 * ────────────────────────────
 * Home feed: reverse-chronological build-log updates from followed
 * users. Backed by GET /api/v1/feed/ (apps/feed) via useFeed.js —
 * cursor-paginated, { results, next_cursor, has_next }.
 *
 * Scope note: the Home Feed design reference (code.html / screen.png)
 * also shows a left "profile summary + network reach" sidebar, a
 * "create update" composer box, and a right "trending professionals /
 * trending projects / achievements" sidebar. The profile-summary +
 * quick-nav sidebar is already covered by the app's persistent
 * Sidebar.jsx (AppLayout renders it on every authenticated page,
 * including this one) — duplicating it here would be redundant. The
 * composer box and the trending/achievements panels have no backing
 * endpoint (no likes/comments model, no trending-professionals or
 * achievements API — Engineering Doc §3.2.3's ProjectUpdate has no
 * engagement fields), so rather than inventing numbers this page keeps
 * the part that maps onto real data — the feed column itself — at a
 * comfortable reading width, the same "drop what isn't backed by data"
 * call ProjectPage.jsx and SearchPage.jsx already made this project.
 *
 * Pagination is scroll-triggered (IntersectionObserver sentinel via
 * useInfiniteScroll.js) rather than a "load more" button, per this
 * session's spec — the design doesn't show a button for the feed.
 */
import { useCallback } from "react";
import { Compass, Rss, AlertCircle } from "lucide-react";

import { useFeed } from "../../hooks/useFeed";
import { useInfiniteScroll } from "../../hooks/useInfiniteScroll";
import { getErrorMessage } from "../../lib/api/errorMessages";

import LinkButton from "../../components/ui/LinkButton";
import FeedCard from "../../components/feed/FeedCard";

import styles from "./FeedPage.module.css";

export default function FeedPage() {
  const {
    data,
    isLoading,
    isError,
    error,
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
  } = useFeed();

  const handleIntersect = useCallback(() => {
    fetchNextPage();
  }, [fetchNextPage]);

  const sentinelRef = useInfiniteScroll({
    onIntersect: handleIntersect,
    enabled: Boolean(hasNextPage) && !isFetchingNextPage && !isLoading,
  });

  const updates = data?.pages?.flatMap((page) => page.results ?? []) ?? [];

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className="text-headline-sm">Home Feed</h1>
        <p className={styles.subtitle}>Updates from the professionals you follow.</p>
      </header>

      {isError ? (
        <div className={styles.errorState} role="alert">
          <AlertCircle size={20} />
          <p>{getErrorMessage(error)}</p>
        </div>
      ) : isLoading ? (
        <FeedSkeleton />
      ) : updates.length === 0 ? (
        <EmptyState />
      ) : (
        <>
          <ol className={styles.list}>
            {updates.map((update) => (
              <li key={update.id}>
                <FeedCard update={update} />
              </li>
            ))}
          </ol>

          {/* Scroll-triggered pagination sentinel — invisible, sits
              below the list and fires fetchNextPage once it enters the
              viewport (400px early, per useInfiniteScroll's rootMargin). */}
          {hasNextPage && <div ref={sentinelRef} aria-hidden="true" />}

          {isFetchingNextPage && (
            <div className={styles.inlineLoading} role="status" aria-live="polite">
              <span className={styles.spinner} aria-hidden="true" />
              Loading more updates…
            </div>
          )}

          {!hasNextPage && (
            <p className={styles.endOfFeed}>All caught up.</p>
          )}
        </>
      )}
    </div>
  );
}

function FeedSkeleton() {
  return (
    <ol className={styles.list}>
      {Array.from({ length: 3 }).map((_, i) => (
        <li key={i}>
          <div className={styles.skeletonCard}>
            <div className={styles.skeletonHeaderRow}>
              <div className={`${styles.skeleton} ${styles.skeletonAvatar}`} />
              <div className={styles.skeletonHeaderLines}>
                <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "40%" }} />
                <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "60%" }} />
              </div>
            </div>
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "90%" }} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "70%" }} />
            <div className={`${styles.skeleton} ${styles.skeletonBlock}`} />
          </div>
        </li>
      ))}
    </ol>
  );
}

function EmptyState() {
  return (
    <div className={styles.emptyState}>
      <div className={styles.emptyBlueprint} aria-hidden="true" />
      <div className={styles.emptyContent}>
        <Rss size={28} className={styles.emptyIcon} />
        <p className={styles.emptyTitle}>Your feed is quiet</p>
        <p className={styles.emptyDescription}>
          Follow professionals to see their build-log updates here — or check back
          once the people you follow log some progress.
        </p>
        <LinkButton to="/search" variant="primary" size="sm" className={styles.emptyCta}>
          <Compass size={16} />
          Find people to follow
        </LinkButton>
      </div>
    </div>
  );
}
