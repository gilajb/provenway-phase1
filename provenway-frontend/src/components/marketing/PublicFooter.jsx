/**
 * src/components/marketing/PublicFooter.jsx
 * ─────────────────────────────────────────────
 * Shared footer for all public marketing pages. Extracted from
 * Landing.jsx. The "Solutions" column is the one column with real
 * routes — Product/Company/Resources stay placeholder "#" links,
 * unchanged from before, out of scope for this pass.
 */
import { Link } from "react-router-dom";
import { Globe, Share2 } from "lucide-react";
import styles from "./PublicFooter.module.css";

const FOOTER_COLUMNS = [
  {
    heading: "Product",
    links: ["Build Logs", "Verification Hub", "Portfolio Designer", "Integrations"],
  },
  {
    heading: "Solutions",
    links: [
      { label: "For Professionals", to: "/for-professionals" },
      { label: "For Construction Firms", to: "/for-construction-firms" },
      { label: "For Architects", to: "/for-architects" },
      { label: "Educational Access", to: "/educational-access" },
    ],
  },
  {
    heading: "Company",
    links: ["About Us", "Careers", "Verification Standards", "Contact"],
  },
  {
    heading: "Resources",
    links: ["Case Studies", "Industry Reports", "Blog", "Support Center"],
  },
];

export default function PublicFooter() {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerInner}>
        <div className={styles.footerGrid}>
          <div className={styles.footerBrandCol}>
            <span className={styles.footerBrand}>Provenway</span>
            <p className={styles.footerTagline}>
              The construction industry&apos;s standard for verified documentation and
              professional portfolios.
            </p>
            <div className={styles.footerSocial}>
              <a href="#" className={styles.footerSocialIcon} aria-label="Website">
                <Globe size={16} />
              </a>
              <a href="#" className={styles.footerSocialIcon} aria-label="Share">
                <Share2 size={16} />
              </a>
            </div>
          </div>

          {FOOTER_COLUMNS.map((col) => (
            <div key={col.heading}>
              <h5 className={styles.footerHeading}>{col.heading}</h5>
              <ul className={styles.footerLinks}>
                {col.links.map((link) => {
                  const isRoute = typeof link === "object";
                  const label = isRoute ? link.label : link;
                  return (
                    <li key={label}>
                      {isRoute ? (
                        <Link to={link.to} className={styles.footerLink}>
                          {label}
                        </Link>
                      ) : (
                        <a href="#" className={styles.footerLink}>
                          {label}
                        </a>
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>

        <div className={styles.footerBottom}>
          <p className={styles.footerCopyright}>© 2026 Provenway. All rights reserved.</p>
          <div className={styles.footerLegal}>
            <a href="#" className={styles.footerLegalLink}>
              Privacy Policy
            </a>
            <a href="#" className={styles.footerLegalLink}>
              Terms of Service
            </a>
            <a href="#" className={styles.footerLegalLink}>
              Trust &amp; Security
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
