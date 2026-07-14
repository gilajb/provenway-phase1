/**
 * src/utils/formatCurrency.js
 * ───────────────────────────
 * Currency formatting (KES primary, USD secondary — Engineering Doc §1.7).
 */

export function formatKES(amount) {
  if (amount == null) return "—";
  return new Intl.NumberFormat("en-KE", {
    style: "currency",
    currency: "KES",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatUSD(amount) {
  if (amount == null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
  }).format(amount);
}

export function formatSalaryRange(min, max) {
  if (!min && !max) return "Salary not specified";
  if (!max) return `From ${formatKES(min)}`;
  if (!min) return `Up to ${formatKES(max)}`;
  return `${formatKES(min)} – ${formatKES(max)}`;
}
