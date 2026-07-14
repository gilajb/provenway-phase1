/**
 * src/components/project/AddUpdateModal.jsx
 * ─────────────────────────────────────────────
 * Owner-only "Add Update" form. Two-step submit:
 *   1. POST /projects/{id}/updates/ — creates the ProjectUpdate itself
 *      (title, body, entry_type, entry_date). created_at is server-set
 *      and never sent from here (Engineering Doc §3.2.3 / Build Plan
 *      red lines).
 *   2. Photos (if any) are uploaded direct-to-Cloudinary — file bytes
 *      never pass through Django (§4.2.2) — then each result is
 *      registered via POST /projects/{id}/updates/{uid}/photos/ with
 *      its sequence_order (0-based, upload order).
 *
 * Deviation flagged for review: the Engineering Doc's Phase-2 plan calls
 * for a rich-text editor (Quill/Tiptap) for the body field, but neither
 * is in package.json yet. This uses a plain Textarea for now — body is
 * still sent as plain text, which the server's bleach whitelist accepts
 * fine, it just isn't formatted. Swap in a rich-text component here once
 * one is added to the project.
 *
 * Visual restyle (Build Log Experience design, this session): markup and
 * CSS updated to match the design reference — the entry-type <select>
 * was swapped for the icon-chip EntryTypeSelector, and the photo picker
 * was split into a dedicated AddPhotoTile / PhotoPreviewTile pair styled
 * after DESIGN.md's blueprint-grid image placeholder. None of the state,
 * validation, or API-calling logic below changed.
 */
import { useState } from "react";
import { AlertCircle } from "lucide-react";

import Modal from "../ui/Modal";
import Input from "../ui/Input";
import Textarea from "../ui/Textarea";
import Button from "../ui/Button";
import EntryTypeSelector from "./EntryTypeSelector";
import PhotoPreviewTile, { AddPhotoTile } from "./PhotoUploadTile";
import { uploadMultipleToCloudinary } from "../../lib/cloudinary/upload";
import { getErrorMessage, getFieldErrors } from "../../lib/api/errorMessages";
import styles from "./AddUpdateModal.module.css";

const MAX_PHOTOS = 10;
const EMPTY_FORM = { title: "", body: "", entry_type: "daily_log", entry_date: "" };

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

export default function AddUpdateModal({ isOpen, onClose, createUpdate, addPhoto }) {
  const [form, setForm] = useState({ ...EMPTY_FORM, entry_date: todayISO() });
  const [files, setFiles] = useState([]);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [stage, setStage] = useState(null); // null | "saving" | "uploading"

  function resetAndClose() {
    setForm({ ...EMPTY_FORM, entry_date: todayISO() });
    setFiles([]);
    setFieldErrors({});
    setFormError(null);
    setStage(null);
    onClose();
  }

  function updateField(field, val) {
    setForm((f) => ({ ...f, [field]: val }));
    if (fieldErrors[field]) setFieldErrors((f) => ({ ...f, [field]: null }));
  }

  function handleFilesSelected(e) {
    const selected = Array.from(e.target.files ?? []);
    setFiles((prev) => [...prev, ...selected].slice(0, MAX_PHOTOS));
    e.target.value = "";
  }

  function removeFile(index) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError(null);

    const payload = {
      title: form.title.trim(),
      body: form.body.trim(),
      entry_type: form.entry_type,
      entry_date: form.entry_date,
    };

    try {
      setStage("saving");
      const created = await createUpdate.mutateAsync(payload);

      if (files.length > 0) {
        setStage("uploading");
        const uploaded = await uploadMultipleToCloudinary(files);
        for (let i = 0; i < uploaded.length; i += 1) {
          const result = uploaded[i];
          // eslint-disable-next-line no-await-in-loop
          await addPhoto.mutateAsync({
            updateId: created.id,
            photo: {
              cloudinary_public_id: result.public_id,
              url: result.secure_url ?? result.url,
              sequence_order: i,
            },
          });
        }
      }

      resetAndClose();
    } catch (err) {
      setFieldErrors(getFieldErrors(err));
      setFormError(getErrorMessage(err));
    } finally {
      setStage(null);
    }
  }

  const isBusy = createUpdate.isPending || addPhoto.isPending || stage !== null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={resetAndClose}
      title="Add update"
      footer={
        <>
          <Button variant="ghost" onClick={resetAndClose} disabled={isBusy}>
            Cancel
          </Button>
          <Button type="submit" form="add-update-form" loading={isBusy}>
            {stage === "uploading" ? "Uploading photos…" : "Post update"}
          </Button>
        </>
      }
    >
      {formError && (
        <div className={styles.errorBanner} role="alert">
          <AlertCircle size={16} />
          <span>{formError}</span>
        </div>
      )}

      <form id="add-update-form" onSubmit={handleSubmit} className={styles.form} noValidate>
        <Input
          label="Title"
          value={form.title}
          error={fieldErrors.title}
          placeholder="e.g. Level 8 floor slab completion"
          onChange={(e) => updateField("title", e.target.value)}
          required
        />

        <EntryTypeSelector
          value={form.entry_type}
          onChange={(val) => updateField("entry_type", val)}
          error={fieldErrors.entry_type}
        />

        <Input
          label="Date"
          type="date"
          value={form.entry_date}
          error={fieldErrors.entry_date}
          onChange={(e) => updateField("entry_date", e.target.value)}
          required
        />

        <Textarea
          label="Details"
          value={form.body}
          rows={5}
          error={fieldErrors.body}
          placeholder="Describe the work completed, materials used, any deviations…"
          onChange={(e) => updateField("body", e.target.value)}
        />

        <div className={styles.photoSection}>
          <div className={styles.photoHeader}>
            <span className={styles.photoLabel}>Photos</span>
            <span className={styles.photoCount}>
              {files.length}/{MAX_PHOTOS}
            </span>
          </div>

          <div className={styles.photoGrid}>
            {files.map((file, i) => (
              <PhotoPreviewTile
                key={`${file.name}-${i}`}
                file={file}
                onRemove={() => removeFile(i)}
              />
            ))}

            {files.length < MAX_PHOTOS && (
              <AddPhotoTile onFilesSelected={handleFilesSelected} disabled={isBusy} />
            )}
          </div>
        </div>
      </form>
    </Modal>
  );
}
