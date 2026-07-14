/**
 * src/components/project/PhotoUploadTile.jsx
 * ─────────────────────────────────────────────
 * Photo grid tiles for AddUpdateModal, extracted so the upload UI can
 * match the Build Log Experience design's "Project Imagery Holder"
 * treatment (a blueprint-grid-textured placeholder) without bloating
 * the modal. Two pieces:
 *   - AddPhotoTile: the dashed trigger tile that opens the file picker.
 *   - PhotoPreviewTile (default export): a selected-but-not-yet-uploaded
 *     photo with a remove control.
 * Purely presentational — file selection/removal logic stays in
 * AddUpdateModal exactly as it was.
 */
import { ImagePlus, X } from "lucide-react";
import styles from "./PhotoUploadTile.module.css";

export function AddPhotoTile({ onFilesSelected, disabled }) {
  return (
    <label className={styles.addTile} data-disabled={disabled || undefined}>
      <span className={styles.blueprintGrid} aria-hidden="true" />
      <ImagePlus size={18} className={styles.addIcon} />
      <span className={styles.addLabel}>Add photos</span>
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp"
        multiple
        onChange={onFilesSelected}
        disabled={disabled}
        hidden
      />
    </label>
  );
}

export default function PhotoPreviewTile({ file, onRemove }) {
  return (
    <div className={styles.previewTile}>
      <img src={URL.createObjectURL(file)} alt="" />
      <button
        type="button"
        className={styles.removeBtn}
        onClick={onRemove}
        aria-label="Remove photo"
      >
        <X size={12} />
      </button>
    </div>
  );
}
