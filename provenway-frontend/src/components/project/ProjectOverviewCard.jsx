/**
 * src/components/project/ProjectOverviewCard.jsx
 * ───────────────────────────────────────────────────
 * "Project Overview" card from the design reference: description +
 * a row of stat tiles. The mockup's tiles (Budget Status, Safety Rating)
 * aren't backed by any field on the Project model (Engineering Doc
 * §3.2.3), so this uses only real data: start/end date, status, and
 * disciplines — same "don't invent data" approach as ProfilePage's
 * ComingSoonCard for unbuilt features.
 */
import { FileText } from "lucide-react";
import { formatDate } from "../../utils/dates";
import { disciplineLabel } from "../../utils/disciplines";
import { projectStatusLabel } from "../../utils/projectEnums";
import styles from "./ProjectOverviewCard.module.css";

export default function ProjectOverviewCard({ project }) {
  const disciplines = project.disciplines ?? [];

  return (
    <div className={styles.card}>
      <h2 className={styles.heading}>
        <FileText size={18} />
        Project Overview
      </h2>

      {project.description ? (
        <p className={styles.description}>{project.description}</p>
      ) : (
        <p className={styles.noDescription}>No description added yet.</p>
      )}

      <div className={styles.statGrid}>
        <div className={styles.stat}>
          <p className={styles.statLabel}>Start Date</p>
          <p className={styles.statValue}>{formatDate(project.start_date) || "—"}</p>
        </div>
        <div className={styles.stat}>
          <p className={styles.statLabel}>End Date</p>
          <p className={styles.statValue}>
            {formatDate(project.end_date) || (project.status === "active" ? "Ongoing" : "—")}
          </p>
        </div>
        <div className={styles.stat}>
          <p className={styles.statLabel}>Status</p>
          <p className={styles.statValue}>{projectStatusLabel(project.status)}</p>
        </div>
        <div className={styles.stat}>
          <p className={styles.statLabel}>Disciplines</p>
          <p className={styles.statValue}>
            {disciplines.length > 0
              ? disciplines.map(disciplineLabel).join(", ")
              : "—"}
          </p>
        </div>
      </div>
    </div>
  );
}
