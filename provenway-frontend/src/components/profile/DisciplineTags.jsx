/**
 * src/components/profile/DisciplineTags.jsx
 * ───────────────────────────────────────────
 * Renders a list of discipline tags for a user or project.
 */

import Badge from "../ui/Badge";
import { disciplineLabel } from "../../utils/disciplines";
import styles from "./DisciplineTags.module.css";

export default function DisciplineTags({ disciplines = [], max }) {
  const shown = max ? disciplines.slice(0, max) : disciplines;
  const overflow = max && disciplines.length > max ? disciplines.length - max : 0;

  return (
    <div className={styles.tags}>
      {shown.map((d) => (
        <Badge key={d} variant="primary">
          {disciplineLabel(d)}
        </Badge>
      ))}
      {overflow > 0 && (
        <Badge variant="muted">+{overflow} more</Badge>
      )}
    </div>
  );
}
