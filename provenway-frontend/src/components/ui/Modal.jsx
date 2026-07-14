/**
 * src/components/ui/Modal.jsx
 * ─────────────────────────────
 * Generic modal primitive (Level 2 elevation per DESIGN.md). Closes on
 * Escape, backdrop click, or the X button. No existing modal component
 * was found in src/components/ui/, so this is new — reuse it rather than
 * building another one-off dialog.
 */
import { useEffect } from "react";
import { X } from "lucide-react";
import { clsx } from "clsx";
import styles from "./Modal.module.css";

export default function Modal({ isOpen, onClose, title, children, footer, className }) {
  useEffect(() => {
    if (!isOpen) return undefined;

    function handleKeyDown(e) {
      if (e.key === "Escape") onClose?.();
    }

    document.addEventListener("keydown", handleKeyDown);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className={styles.backdrop}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose?.();
      }}
    >
      <div className={clsx(styles.modal, className)} role="dialog" aria-modal="true" aria-label={title}>
        <div className={styles.header}>
          <h2 className={styles.title}>{title}</h2>
          <button type="button" className={styles.closeBtn} onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <div className={styles.body}>{children}</div>

        {footer && <div className={styles.footer}>{footer}</div>}
      </div>
    </div>
  );
}
