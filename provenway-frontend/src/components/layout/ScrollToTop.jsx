/**
 * src/components/layout/ScrollToTop.jsx
 * ─────────────────────────────────────────
 * React Router's client-side navigation doesn't reset scroll position
 * the way a full page load would — without this, clicking a link that
 * lives near the bottom of a page (e.g. a footer link) lands you at the
 * same scroll offset on the new page, which can put you anywhere from
 * mid-page to its own footer instead of at the top.
 *
 * When a hash is present (e.g. nav's "Solutions" link -> "/#solutions"),
 * this scrolls to that element itself rather than deferring to the
 * browser's native load-time anchor scroll — that native behaviour
 * fires before React has rendered anything (the target id doesn't
 * exist yet), so on a fresh/full page load it silently does nothing.
 */
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export default function ScrollToTop() {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    if (hash) {
      document.getElementById(hash.slice(1))?.scrollIntoView();
      return;
    }
    window.scrollTo(0, 0);
  }, [pathname, hash]);

  return null;
}
