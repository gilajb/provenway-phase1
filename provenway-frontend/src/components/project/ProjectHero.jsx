/**
 * src/components/project/ProjectHero.jsx
 * ──────────────────────────────────────────
 * Header block for the project detail page. The design reference
 * (screen.png / code.html) uses a full-bleed photographic hero, but
 * Project has no image_url field anywhere in the schema (Engineering
 * Doc §3.2.3) — there's no real photo to show without inventing one.
 * This uses the same "no image present" blueprint-grid treatment
 * ComingSoonCard already established, so it reads as an intentional
 * architectural surface rather than a broken image.
 */
import { MapPin } from "lucide-react";
import Badge from "../ui/Badge";
import VisibilityBadge from "./VisibilityBadge";
import { projectStatusLabel, projectStatusBadgeVariant } from "../../utils/projectEnums";
import styles from "./ProjectHero.module.css";

export default function ProjectHero({ project, isOwner }) {
  return (
    <div className={styles.hero}>
      <div className={styles.blueprint} aria-hidden="true" />
      <div className={styles.content}>
        <div className={styles.badgeRow}>
          <Badge variant={projectStatusBadgeVariant(project.status)}>
            {projectStatusLabel(project.status)}
          </Badge>
          {isOwner && <VisibilityBadge visibility={project.visibility} />}
        </div>

        <h1 className={styles.title}>{project.title}</h1>

        {project.location_text && (
          <p className={styles.location}>
            <MapPin size={16} />
            {project.location_text}
          </p>
        )}
      </div>
    </div>
  );
}
