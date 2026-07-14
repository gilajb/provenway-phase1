/**
 * src/pages/main/SearchPage.jsx
 * ──────────────────────────────
 * Professional directory search, backed by GET /api/v1/users/ via
 * useDirectorySearch (src/hooks/useDirectorySearch.js).
 *
 * Design note: the Discovery design reference (Professional_Discovery
 * code.html / screen.png) also shows a "Projects" / "Verification
 * Requests" tab set, a category sidebar with per-role counts, and a
 * "Top Verified Firms" panel. None of those are backed by a real
 * endpoint yet (there's no per-discipline count endpoint, no firms
 * app, and this session's API is Professionals-only), so rather than
 * inventing numbers this page keeps the design's search-terminal header,
 * pill filter row, and professional card grid — the parts that map onto
 * real data — and drops the rest. Discipline chips reuse the existing
 * DisciplineSelector (from the profile-edit flow) instead of a new
 * component, per the pill-chip spec in DESIGN.md.
 */
import { useState } from "react";
import { Search as SearchIcon, MapPin, CheckCircle2, SearchX, ChevronLeft, ChevronRight } from "lucide-react";

import { useDirectorySearch } from "../../hooks/useDirectorySearch";
import { getErrorMessage } from "../../lib/api/errorMessages";

import Button from "../../components/ui/Button";
import DisciplineSelector from "../../components/profile/DisciplineSelector";
import ProfessionalCard from "../../components/search/ProfessionalCard";

import styles from "./SearchPage.module.css";

export default function SearchPage() {
  const [q, setQ] = useState("");
  const [disciplines, setDisciplines] = useState([]);
  const [location, setLocation] = useState("");
  const [verified, setVerified] = useState(false);

  const {
    results,
    count,
    offset,
    pageSize,
    hasNext,
    hasPrevious,
    nextPage,
    previousPage,
    isLoading,
    isFetching,
    isError,
    error,
  } = useDirectorySearch({ q, disciplines, location, verified });

  const hasActiveFilters = q || disciplines.length > 0 || location || verified;

  function clearFilters() {
    setQ("");
    setDisciplines([]);
    setLocation("");
    setVerified(false);
  }

  const rangeStart = count === 0 ? 0 : offset + 1;
  const rangeEnd = Math.min(offset + pageSize, count);

  return (
    <div className={styles.page}>
      {/* ── Header / search terminal ─────────────────────────────────── */}
      <header className={styles.header}>
        <div className={styles.blueprint} aria-hidden="true" />
        <div className={styles.headerContent}>
          <h1 className={styles.title}>Find professionals</h1>
          <p className={styles.subtitle}>Search by name, discipline, or location.</p>

          <div className={styles.searchBar}>
            <SearchIcon size={20} className={styles.searchIcon} aria-hidden="true" />
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Find professionals by name or headline"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              aria-label="Search professionals"
            />
          </div>

          <div className={styles.filterRow}>
            <div className={styles.locationFilter}>
              <MapPin size={16} className={styles.locationIcon} aria-hidden="true" />
              <input
                type="text"
                className={styles.locationInput}
                placeholder="Location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                aria-label="Filter by location"
              />
            </div>

            <button
              type="button"
              className={`${styles.verifiedToggle} ${verified ? styles.verifiedToggleActive : ""}`}
              onClick={() => setVerified((v) => !v)}
              aria-pressed={verified}
            >
              <CheckCircle2 size={16} />
              Verified only
            </button>

            {hasActiveFilters && (
              <button type="button" className={styles.clearFilters} onClick={clearFilters}>
                Clear filters
              </button>
            )}
          </div>

          <div className={styles.disciplineFilter}>
            <DisciplineSelector value={disciplines} onChange={setDisciplines} label="Discipline" />
          </div>
        </div>
      </header>

      {/* ── Results ───────────────────────────────────────────────────── */}
      {isError ? (
        <div className={styles.errorState} role="alert">
          <p>{getErrorMessage(error)}</p>
        </div>
      ) : isLoading ? (
        <ResultsSkeleton />
      ) : results.length === 0 ? (
        <EmptyState hasActiveFilters={hasActiveFilters} onClear={clearFilters} />
      ) : (
        <>
          <div className={`${styles.grid} ${isFetching ? styles.gridFetching : ""}`}>
            {results.map((person) => (
              <ProfessionalCard key={person.id ?? person.user_id} person={person} />
            ))}
          </div>

          <div className={styles.pagination}>
            <Button
              variant="secondary"
              size="sm"
              onClick={previousPage}
              disabled={!hasPrevious || isFetching}
            >
              <span className={styles.pageBtnContent}>
                <ChevronLeft size={16} />
                Previous
              </span>
            </Button>

            <p className={styles.pageStatus}>
              Showing {rangeStart}–{rangeEnd} of {count} professionals
            </p>

            <Button
              variant="secondary"
              size="sm"
              onClick={nextPage}
              disabled={!hasNext || isFetching}
            >
              <span className={styles.pageBtnContent}>
                Next
                <ChevronRight size={16} />
              </span>
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

function ResultsSkeleton() {
  return (
    <div className={styles.grid}>
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className={styles.skeletonCard}>
          <div className={`${styles.skeleton} ${styles.skeletonAvatar}`} />
          <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "70%" }} />
          <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "50%" }} />
          <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "90%", marginTop: "var(--space-md)" }} />
        </div>
      ))}
    </div>
  );
}

function EmptyState({ hasActiveFilters, onClear }) {
  return (
    <div className={styles.emptyState}>
      <div className={styles.emptyBlueprint} aria-hidden="true" />
      <div className={styles.emptyContent}>
        <SearchX size={28} className={styles.emptyIcon} />
        <p className={styles.emptyTitle}>No professionals found</p>
        <p className={styles.emptyDescription}>
          {hasActiveFilters
            ? "Try a different name, location, or fewer filters."
            : "No professionals are listed in the directory yet."}
        </p>
        {hasActiveFilters && (
          <Button variant="secondary" size="sm" onClick={onClear} className={styles.emptyClearButton}>
            Clear filters
          </Button>
        )}
      </div>
    </div>
  );
}
