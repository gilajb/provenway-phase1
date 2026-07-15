/**
 * src/components/marketing/PublicNav.jsx
 * ─────────────────────────────────────────
 * Shared top nav for all public marketing pages (Landing + the 4
 * audience pages under /for-*). Extracted from Landing.jsx so the 5
 * pages that need this chrome don't each duplicate it.
 */
import { Link } from "react-router-dom";
import LinkButton from "../ui/LinkButton";
import styles from "./PublicNav.module.css";

const NAV_LINKS = [
  { label: "Explore", href: "/" },
  // Absolute path + hash (not a bare "#solutions") so this resolves
  // correctly from every public route, not just from "/" itself.
  { label: "Solutions", href: "/#solutions" },
  { label: "Firms", href: "#" },
  { label: "Pricing", href: "#" },
];

export default function PublicNav() {
  return (
    <nav className={styles.nav}>
      <div className={styles.navInner}>
        <div className={styles.navLeft}>
          <span className={styles.brand}>Provenway</span>
          <div className={styles.navLinks}>
            {NAV_LINKS.map(({ label, href }, i) => (
              <a key={label} href={href} className={i === 0 ? styles.navLinkActive : styles.navLink}>
                {label}
              </a>
            ))}
          </div>
        </div>
        <div className={styles.navRight}>
          <Link to="/login" className={styles.signInLink}>
            Sign In
          </Link>
          <LinkButton to="/register" variant="primary" size="md">
            Sign Up
          </LinkButton>
        </div>
      </div>
    </nav>
  );
}
