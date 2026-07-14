/**
 * src/components/layout/Navbar.jsx
 * ─────────────────────────────────
 * Top navigation bar. Glassmorphism treatment per DESIGN.md.
 */
import { Link, useNavigate } from "react-router-dom";
import { Bell, Search, LogOut } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import useNotificationStore from "../../stores/notificationStore";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const { user, logout } = useAuth();
  const unreadCount = useNotificationStore((s) => s.unreadCount);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className={styles.navbar}>
      <div className={styles.inner}>
        <Link to="/feed" className={styles.brand}>Provenway</Link>

        <div className={styles.actions}>
          <Link to="/search" className={styles.iconBtn} aria-label="Search">
            <Search size={20} />
          </Link>

          <Link to="/notifications" className={styles.iconBtn} aria-label="Notifications">
            <Bell size={20} />
            {unreadCount > 0 && (
              <span className={styles.badge}>
                {unreadCount > 99 ? "99+" : unreadCount}
              </span>
            )}
          </Link>

          {user && (
            <Link to={`/profile/${user.id}`} className={styles.avatarLink}>
              {user.avatar_url ? (
                <img src={user.avatar_url} alt={user.display_name} className={styles.avatar} />
              ) : (
                <div className={styles.avatarFallback}>
                  {user.display_name?.[0]?.toUpperCase()}
                </div>
              )}
            </Link>
          )}

          <button onClick={handleLogout} className={styles.iconBtn} aria-label="Log out">
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </nav>
  );
}
