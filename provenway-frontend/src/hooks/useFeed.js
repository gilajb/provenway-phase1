/**
 * src/hooks/useFeed.js
 * ────────────────────
 * Home feed — GET /api/v1/feed/ (apps/feed), cursor-paginated per this
 * session's confirmed contract:
 *   { results: ProjectUpdate[], next_cursor: string | null, has_next: bool }
 * (Not the DRF-default { results, next, previous } shape used elsewhere
 * in this app — e.g. useProjectUpdates.js — so this hook reads
 * `next_cursor` / `has_next` directly instead of parsing an absolute
 * `next` URL.)
 *
 * Infinite-scroll via React Query's useInfiniteQuery: getNextPageParam
 * hands back next_cursor as the next pageParam, and returns undefined
 * (stopping pagination) as soon as has_next is false — even if the
 * server happened to still send a next_cursor value alongside it.
 */
import { useInfiniteQuery } from "@tanstack/react-query";
import { apiClient } from "../lib/api/apiClient";
import { FEED } from "../lib/api/endpoints";

export function useFeed() {
  return useInfiniteQuery({
    queryKey: ["feed"],
    queryFn: ({ pageParam }) => {
      const url = pageParam
        ? `${FEED.HOME}?cursor=${encodeURIComponent(pageParam)}`
        : FEED.HOME;
      return apiClient.get(url);
    },
    initialPageParam: null,
    getNextPageParam: (lastPage) =>
      lastPage?.has_next ? lastPage?.next_cursor ?? undefined : undefined,
    staleTime: 1000 * 30,
  });
}

export default useFeed;
