/**
 * src/components/ui/ConfirmModal.jsx
 * ─────────────────────────────────────
 * Generic yes/no confirmation dialog, built on the shared Modal primitive.
 * No existing confirm dialog was found in src/components/ui/ — reuse this
 * rather than a one-off window.confirm() or a new modal.
 */
import { AlertCircle } from "lucide-react";
import Modal from "./Modal";
import Button from "./Button";
import styles from "./ConfirmModal.module.css";

export default function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title = "Are you sure?",
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  isDanger = true,
  isLoading = false,
}) {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={isLoading}>
            {cancelLabel}
          </Button>
          <Button
            variant={isDanger ? "danger" : "primary"}
            onClick={onConfirm}
            loading={isLoading}
          >
            {confirmLabel}
          </Button>
        </>
      }
    >
      <div className={styles.body}>
        {isDanger && <AlertCircle size={20} className={styles.icon} />}
        {description && <p className={styles.description}>{description}</p>}
      </div>
    </Modal>
  );
}
