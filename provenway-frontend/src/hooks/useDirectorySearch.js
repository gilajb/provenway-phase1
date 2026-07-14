/**
 * src/hooks/useDirectorySearch.js
 * ─────────────────────────────────
 * Professional directory search (GET /api/v1/users/ — offset-paginated).
 * Query params: q, discipline (sent repeated — one `discipline=` per
 * selected value, the standard shape for DRF's request.GET.getlist()),
 * location, verified, limit, offset.
 *
 * Debounce behaviour is intentionally asymmetric, per spec:
 *  - `q` (free-text search) is debounced ~400ms so typing a name doesn't
 *    fire a request per keystroke.
 *  - discipline chips, the verified toggle, and location apply on the
 *    very next render (no debounce) — they're either single clicks
 *    (chips/toggle) or, for location, explicitly called out as an
 *    immediate-apply field for now (no debounce requested).
 *
 * Pagination is offset-based: the hook owns `offset` and resets it to 0
 * whenever any filter (including the debounced q) changes, so switching
 * filters never leaves you stranded on an out-of-range page.
 */
import { useEffect, useRef, useState } from "react";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { apiClient } from "../lib/api/apiClient";
import { USERS } from "../lib/api/endpoints";

export const PAGE_SIZE = 12;
const DEBOUNCE_MS = 400;

function buildQueryString({ debouncedQ, disciplines, location, verified, offset }) {
  const params = new URLSearchParams();
  if (debouncedQ) params.set("q", debouncedQ);
  disciplines.forEach((d) => params.append("discipline", d));
  if (location) params.set("location", location);
  if (verified) params.set("verified", "true");
  params.set("limit", String(PAGE_SIZE));
  params.set("offset", String(offset));
  return params.toString();
}

/**
 * @param {object} filters
 * @param {string} filters.q - raw (un-debounced) search text
 * @param {string[]} filters.disciplines - selected discipline values
 * @param {string} filters.location - free-text location filter
 * @param {boolean} filters.verified - verified-only toggle
 */
export function useDirectorySearch({ q = "", disciplines = [], location = "", verified = false } = {}) {
  const [debouncedQ, setDebouncedQ] = useState(q);
  const [offset, setOffset] = useState(0);
  const isFirstRun = useRef(true);

  // Debounce q only.
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQ(q), DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [q]);

  // Any filter change (once settled) resets pagination back to page 1.
  // Discipline array identity changes every render from the caller, so
  // compare by joined value rather than reference.
  const disciplineKey = disciplines.join(",");
  useEffect(() => {
    if (isFirstRun.current) {
      isFirstRun.current = false;
      return;
    }
    setOffset(0);
  }, [debouncedQ, disciplineKey, location, verified]);

  const queryString = buildQueryString({ debouncedQ, disciplines, location, verified, offset });

  const query = useQuery({
    queryKey: ["directory-search", debouncedQ, disciplineKey, location, verified, offset],
    queryFn: () => apiClient.get(`${USERS.SEARCH}?${queryString}`),
    placeholderData: keepPreviousData,
    staleTime: 1000 * 30,
  });

  const results = query.data?.results ?? [];
  const count = query.data?.count ?? 0;
  const hasNext = Boolean(query.data?.next) || offset + PAGE_SIZE < count;
  const hasPrevious = offset > 0;

  return {
    ...query,
    results,
    count,
    offset,
    pageSize: PAGE_SIZE,
    hasNext,
    hasPrevious,
    nextPage: () => setOffset((prev) => (hasNext ? prev + PAGE_SIZE : prev)),
    previousPage: () => setOffset((prev) => Math.max(0, prev - PAGE_SIZE)),
    // True while the debounce timer hasn't caught up to the latest keystroke —
    // lets the UI show a subtler "searching…" state instead of a full skeleton.
    isDebouncing: q !== debouncedQ,
  };
}

export default useDirectorySearch;
