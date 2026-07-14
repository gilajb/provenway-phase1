/**
 * src/components/layout/Sidebar.jsx
 * ───────────────────────────────────
 * Left navigation sidebar for the authenticated shell.
 * Hidden on mobile (bottom nav to be added in a later iteration).
 */
import { NavLink } from "react-router-dom";
import { Home, Briefcase, FileText, MessageSquare, Search, User } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import styles from "./Sidebar.module.css";

const NAV_ITEMS = [
  { to: "/feed",         icon: Home,          label: "Feed" },
  { to: "/search",       icon: Search,        label: "Discover" },
  { to: "/jobs",         icon: Briefcase,     label: "Jobs" },
  { to: "/tenders",      icon: FileText,      label: "Tenders" },
  { to: "/messages",     icon: MessageSquare, label: "Messages" },
];

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className={styles.sidebar}>
      <nav className={styles.nav}>
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [styles.link, isActive ? styles.active : ""].filter(Boolean).join(" ")
            }
          >
            <Icon size={20} />
            <span className={styles.label}>{label}</span>
          </NavLink>
        ))}

        {user && (
          <NavLink
            to={`/profile/${user.id}`}
            className={({ isActive }) =>
              [styles.link, isActive ? styles.active : ""].filter(Boolean).join(" ")
            }
          >
            <User size={20} />
            <span className={styles.label}>Profile</span>
          </NavLink>
        )}
      </nav>
    </aside>
  );
}
