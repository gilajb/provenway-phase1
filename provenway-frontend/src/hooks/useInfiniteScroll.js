/**
 * src/hooks/useInfiniteScroll.js
 * ───────────────────────────────
 * Small reusable hook that fires a callback (fetchNextPage) when a
 * sentinel element scrolls into view — used instead of a manual
 * "load more" button wherever the design calls for continuous scroll
 * (the Home Feed, per this session's spec; UpdateTimeline.jsx keeps
 * its explicit button since the Build Log design shows one).
 *
 * Usage:
 *   const sentinelRef = useInfiniteScroll({
 *     onIntersect: fetchNextPage,
 *     enabled: hasNextPage && !isFetchingNextPage,
 *   });
 *   ...
 *   <div ref={sentinelRef} />
 */
import { useEffect, useRef } from "react";

export function useInfiniteScroll({ onIntersect, enabled = true, rootMargin = "400px" } = {}) {
  const sentinelRef = useRef(null);

  useEffect(() => {
    const node = sentinelRef.current;
    if (!node || !enabled) return undefined;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          onIntersect?.();
        }
      },
      { rootMargin }
    );

    observer.observe(node);
    return () => observer.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, onIntersect]);

  return sentinelRef;
}

export default useInfiniteScroll;
