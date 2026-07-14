/**
 * src/components/project/VisibilityBadge.jsx
 * ──────────────────────────────────────────────
 * Pill indicator for Project.visibility (public / connections / private).
 * Per the task spec this is shown to the owner only — callers decide
 * whether to render it, this component just handles the icon + label.
 */
import { Globe2, Users, Lock } from "lucide-react";
import Badge from "../ui/Badge";
import { projectVisibilityLabel } from "../../utils/projectEnums";

const ICONS = {
  public: Globe2,
  connections: Users,
  private: Lock,
};

const VARIANTS = {
  public: "success",
  connections: "primary",
  private: "muted",
};

export default function VisibilityBadge({ visibility }) {
  const Icon = ICONS[visibility] ?? Lock;
  return (
    <Badge variant={VARIANTS[visibility] ?? "muted"}>
      <Icon size={12} />
      {projectVisibilityLabel(visibility)}
    </Badge>
  );
}
