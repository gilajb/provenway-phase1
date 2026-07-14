/**
 * src/utils/dates.js
 * ──────────────────
 * Date formatting helpers for the Provenway UI.
 * Using date-fns for lightweight, tree-shakeable date ops.
 */
import { format, formatDistanceToNow, parseISO, isValid } from "date-fns";

/** "14 Jun 2024" */
export function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = typeof dateStr === "string" ? parseISO(dateStr) : dateStr;
  return isValid(d) ? format(d, "d MMM yyyy") : "";
}

/** "14 Jun 2024, 09:30" */
export function formatDateTime(dateStr) {
  if (!dateStr) return "";
  const d = typeof dateStr === "string" ? parseISO(dateStr) : dateStr;
  return isValid(d) ? format(d, "d MMM yyyy, HH:mm") : "";
}

/** "3 days ago", "just now" */
export function timeAgo(dateStr) {
  if (!dateStr) return "";
  const d = typeof dateStr === "string" ? parseISO(dateStr) : dateStr;
  return isValid(d) ? formatDistanceToNow(d, { addSuffix: true }) : "";
}

/** "Jun 2024" — for project timelines */
export function formatMonth(dateStr) {
  if (!dateStr) return "";
  const d = typeof dateStr === "string" ? parseISO(dateStr) : dateStr;
  return isValid(d) ? format(d, "MMM yyyy") : "";
}
