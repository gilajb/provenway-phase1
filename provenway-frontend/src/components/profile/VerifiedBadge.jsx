/**
 * src/components/profile/VerifiedBadge.jsx
 * ──────────────────────────────────────────
 * Teal "Verified" pill displayed on verified profiles, search results,
 * and build log entries.
 */

import { CheckCircle } from "lucide-react";
import Badge from "../ui/Badge";

export default function VerifiedBadge({ size = 12 }) {
  return (
    <Badge variant="success">
      <CheckCircle size={size} />
      Verified
    </Badge>
  );
}
