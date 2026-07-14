/**
 * src/components/profile/DisciplineSelector.jsx
 * ────────────────────────────────────────────────
 * Multi-select toggle grid over the controlled discipline taxonomy
 * (utils/disciplines.js). Used in the profile edit form — renders as
 * pill toggles styled consistently with DisciplineTags/Badge.
 */
import { clsx } from "clsx";
import { DISCIPLINE_OPTIONS } from "../../utils/disciplines";
import styles from "./DisciplineSelector.module.css";

export default function DisciplineSelector({ value = [], onChange, label = "Disciplines" }) {
  function toggle(disciplineValue) {
    if (value.includes(disciplineValue)) {
      onChange(value.filter((d) => d !== disciplineValue));
    } else {
      onChange([...value, disciplineValue]);
    }
  }

  return (
    <div className={styles.wrapper}>
      {label && <span className={styles.label}>{label}</span>}
      <div className={styles.grid}>
        {DISCIPLINE_OPTIONS.map(({ value: optionValue, label: optionLabel }) => {
          const selected = value.includes(optionValue);
          return (
            <button
              key={optionValue}
              type="button"
              onClick={() => toggle(optionValue)}
              className={clsx(styles.pill, selected && styles.selected)}
              aria-pressed={selected}
            >
              {optionLabel}
            </button>
          );
        })}
      </div>
    </div>
  );
}
