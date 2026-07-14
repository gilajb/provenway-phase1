/**
 * src/utils/disciplines.js
 * ────────────────────────
 * Human-readable labels for the discipline taxonomy (Engineering Doc §3.2.1).
 */

export const DISCIPLINE_LABELS = {
  architect:           "Architect",
  civil_engineer:      "Civil Engineer",
  structural_engineer: "Structural Engineer",
  qs:                  "Quantity Surveyor",
  contractor:          "Contractor",
  site_supervisor:     "Site Supervisor",
  project_manager:     "Project Manager",
  interior_designer:   "Interior Designer",
  mep_engineer:        "MEP Engineer",
};

export const DISCIPLINE_OPTIONS = Object.entries(DISCIPLINE_LABELS).map(
  ([value, label]) => ({ value, label })
);

export function disciplineLabel(value) {
  return DISCIPLINE_LABELS[value] ?? value;
}
