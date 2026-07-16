/**
 * src/components/project/ExportPdfButton.jsx
 * ──────────────────────────────────────────────
 * Owner-only toolbar action: trigger a PDF portfolio export, poll until
 * it's ready, then swap to a download link. Split out of ProjectPage.jsx
 * the same way AddUpdateModal/EditProjectModal already are.
 */
import { Download, FileText, Loader2 } from "lucide-react";
import Button from "../ui/Button";
import { useProjectExport } from "../../hooks/useProjectExport";
import { getErrorMessage } from "../../lib/api/errorMessages";
import styles from "./ExportPdfButton.module.css";

export default function ExportPdfButton({ projectId }) {
  const { startExport, isStarting, startError, status, pdfUrl, error } =
    useProjectExport(projectId);

  const isProcessing = isStarting || status === "processing";

  if (status === "completed" && pdfUrl) {
    return (
      <a href={pdfUrl} download className={styles.downloadLink}>
        <Download size={14} />
        Download PDF
      </a>
    );
  }

  return (
    <div className={styles.wrapper}>
      <Button variant="ghost" size="sm" onClick={startExport} disabled={isProcessing}>
        {isProcessing ? <Loader2 size={14} className={styles.spinner} /> : <FileText size={14} />}
        {isProcessing ? "Preparing PDF…" : "Export PDF"}
      </Button>
      {(status === "failed" || startError) && (
        <span className={styles.errorText}>{error ?? getErrorMessage(startError)}</span>
      )}
    </div>
  );
}
