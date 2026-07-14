/**
 * src/components/ui/Avatar.jsx
 * ─────────────────────────────
 * User avatar: shows Cloudinary image if available, initials otherwise.
 */

import styles from "./Avatar.module.css";

function getInitials(name = "") {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

export default function Avatar({ src, name = "", size = 40, className }) {
  // avatar_url from the API is already a complete, ready-to-use Cloudinary
  // URL (server-mediated upload — see apps/profiles), not a public_id, so
  // it's used as-is. (This mirrors how Navbar.jsx already renders it.)
  const url = src || null;
  const initials = getInitials(name);

  return (
    <div
      className={[styles.avatar, className].filter(Boolean).join(" ")}
      style={{ width: size, height: size, fontSize: size * 0.38 }}
      aria-label={name}
      role="img"
    >
      {url ? (
        <img
          src={url}
          alt={name}
          width={size}
          height={size}
          className={styles.img}
          loading="lazy"
        />
      ) : (
        <span className={styles.initials}>{initials || "?"}</span>
      )}
    </div>
  );
}
