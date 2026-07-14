/**
 * src/components/ui/LinkButton.jsx
 * ──────────────────────────────────
 * Renders a react-router <Link> styled exactly like <Button>, reusing
 * Button.module.css. Use this instead of wrapping <Button> in <Link>
 * (which nests an invalid <button> inside an <a>).
 */
import { Link } from "react-router-dom";
import { clsx } from "clsx";
import btnStyles from "./Button.module.css";

export default function LinkButton({
  to,
  children,
  variant = "primary",
  size = "md",
  fullWidth = false,
  className,
  ...props
}) {
  return (
    <Link
      to={to}
      className={clsx(
        btnStyles.btn,
        btnStyles[variant],
        btnStyles[size],
        fullWidth && btnStyles.fullWidth,
        className
      )}
      {...props}
    >
      {children}
    </Link>
  );
}
