/**
 * src/components/project/EntryTypeSelector.jsx
 * ───────────────────────────────────────────────
 * Icon-led chip picker for ProjectUpdate.entry_type, restyled to match
 * the Build Log Experience design reference (icon + label tiles, the
 * same "selected" treatment the mockup uses for its in-progress
 * milestone: a soft blue fill + border rather than a solid pill).
 * Pure presentation — value/onChange contract mirrors a native
 * <select>, so AddUpdateModal's existing form state is untouched.
 */
import { Flag, ClipboardList, AlertTriangle, ShieldCheck, PartyPopper } from "lucide-react";
import { clsx } from "clsx";
import { ENTRY_TYPE_OPTIONS } from "../../utils/projectEnums";
import styles from "./EntryTypeSelector.module.css";

const ICONS = {
  milestone: Flag,
  daily_log: ClipboardList,
  issue: AlertTriangle,
  inspection: ShieldCheck,
  phase_complete: PartyPopper,
};

export default function EntryTypeSelector({ value, onChange, error }) {
  return (
    <div className={styles.wrapper}>
      <span className={styles.label}>Entry type</span>
      <div className={styles.options} role="radiogroup" aria-label="Entry type">
        {ENTRY_TYPE_OPTIONS.map((opt) => {
          const Icon = ICONS[opt.value] ?? ClipboardList;
          const selected = value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              role="radio"
              aria-checked={selected}
              className={clsx(styles.option, selected && styles.selected)}
              onClick={() => onChange(opt.value)}
            >
              <Icon size={16} />
              <span>{opt.label}</span>
            </button>
          );
        })}
      </div>
      {error && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
