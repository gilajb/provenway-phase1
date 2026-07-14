/**
 * src/utils/projectEnums.js
 * ──────────────────────────
 * Human-readable labels for the Project / ProjectUpdate enum fields
 * (Engineering Doc §3.2.3). Mirrors the pattern in utils/disciplines.js.
 */

// ── Project.status (active / completed / paused / cancelled) ──────────────
export const PROJECT_STATUS_LABELS = {
  active: "Active",
  completed: "Completed",
  paused: "Paused",
  cancelled: "Cancelled",
};

export const PROJECT_STATUS_OPTIONS = Object.entries(PROJECT_STATUS_LABELS).map(
  ([value, label]) => ({ value, label })
);

export function projectStatusLabel(value) {
  return PROJECT_STATUS_LABELS[value] ?? value;
}

// Badge variant per status — success (teal) for active/completed, muted otherwise.
export function projectStatusBadgeVariant(value) {
  if (value === "active") return "primary";
  if (value === "completed") return "success";
  return "muted";
}

// ── Project.visibility (public / connections / private) ───────────────────
export const PROJECT_VISIBILITY_LABELS = {
  public: "Public",
  connections: "Connections only",
  private: "Private",
};

export const PROJECT_VISIBILITY_OPTIONS = Object.entries(PROJECT_VISIBILITY_LABELS).map(
  ([value, label]) => ({ value, label })
);

export function projectVisibilityLabel(value) {
  return PROJECT_VISIBILITY_LABELS[value] ?? value;
}

// ── ProjectUpdate.entry_type ───────────────────────────────────────────────
export const ENTRY_TYPE_LABELS = {
  milestone: "Milestone",
  daily_log: "Daily Log",
  issue: "Issue / Resolution",
  inspection: "Inspection Passed",
  phase_complete: "Phase Complete",
};

export const ENTRY_TYPE_OPTIONS = Object.entries(ENTRY_TYPE_LABELS).map(
  ([value, label]) => ({ value, label })
);

export function entryTypeLabel(value) {
  return ENTRY_TYPE_LABELS[value] ?? value;
}
