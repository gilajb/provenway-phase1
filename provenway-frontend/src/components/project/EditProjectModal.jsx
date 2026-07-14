/**
 * src/components/project/EditProjectModal.jsx
 * ───────────────────────────────────────────────
 * Owner-only edit form for Project fields (Engineering Doc §3.2.3):
 * title, description, location_text, status, visibility, start_date,
 * end_date, disciplines. PATCHes /projects/{id}/ via the updateProject
 * mutation from useProject(). Mirrors EditProfileModal's structure.
 */
import { useEffect, useState } from "react";
import { AlertCircle } from "lucide-react";

import Modal from "../ui/Modal";
import Input from "../ui/Input";
import Textarea from "../ui/Textarea";
import Select from "../ui/Select";
import Button from "../ui/Button";
import DisciplineSelector from "../profile/DisciplineSelector";
import { PROJECT_STATUS_OPTIONS, PROJECT_VISIBILITY_OPTIONS } from "../../utils/projectEnums";
import { getErrorMessage, getFieldErrors } from "../../lib/api/errorMessages";
import styles from "./EditProjectModal.module.css";

function buildInitialForm(project) {
  return {
    title: project?.title ?? "",
    description: project?.description ?? "",
    location_text: project?.location_text ?? "",
    status: project?.status ?? "active",
    visibility: project?.visibility ?? "public",
    start_date: project?.start_date ?? "",
    end_date: project?.end_date ?? "",
    disciplines: project?.disciplines ?? [],
  };
}

export default function EditProjectModal({ isOpen, onClose, project, updateProject }) {
  const [form, setForm] = useState(() => buildInitialForm(project));
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setForm(buildInitialForm(project));
      setFieldErrors({});
      setFormError(null);
    }
  }, [isOpen, project]);

  function updateField(field, val) {
    setForm((f) => ({ ...f, [field]: val }));
    if (fieldErrors[field]) setFieldErrors((f) => ({ ...f, [field]: null }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError(null);

    const patch = {
      title: form.title.trim(),
      description: form.description.trim(),
      location_text: form.location_text.trim(),
      status: form.status,
      visibility: form.visibility,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
      disciplines: form.disciplines,
    };

    try {
      await updateProject.mutateAsync(patch);
      onClose();
    } catch (err) {
      setFieldErrors(getFieldErrors(err));
      setFormError(getErrorMessage(err));
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Edit project"
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={updateProject.isPending}>
            Cancel
          </Button>
          <Button type="submit" form="edit-project-form" loading={updateProject.isPending}>
            Save changes
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

      <form id="edit-project-form" onSubmit={handleSubmit} className={styles.form} noValidate>
        <Input
          label="Title"
          value={form.title}
          error={fieldErrors.title}
          onChange={(e) => updateField("title", e.target.value)}
          required
        />

        <Textarea
          label="Description"
          value={form.description}
          rows={4}
          error={fieldErrors.description}
          placeholder="What is this project about?"
          onChange={(e) => updateField("description", e.target.value)}
        />

        <Input
          label="Location"
          value={form.location_text}
          error={fieldErrors.location_text}
          placeholder="e.g. Westlands, Nairobi"
          onChange={(e) => updateField("location_text", e.target.value)}
        />

        <div className={styles.row}>
          <Select
            label="Status"
            value={form.status}
            options={PROJECT_STATUS_OPTIONS}
            error={fieldErrors.status}
            onChange={(e) => updateField("status", e.target.value)}
          />
          <Select
            label="Visibility"
            value={form.visibility}
            options={PROJECT_VISIBILITY_OPTIONS}
            error={fieldErrors.visibility}
            onChange={(e) => updateField("visibility", e.target.value)}
          />
        </div>

        <div className={styles.row}>
          <Input
            label="Start date"
            type="date"
            value={form.start_date ?? ""}
            error={fieldErrors.start_date}
            onChange={(e) => updateField("start_date", e.target.value)}
          />
          <Input
            label="End date"
            type="date"
            value={form.end_date ?? ""}
            error={fieldErrors.end_date}
            onChange={(e) => updateField("end_date", e.target.value)}
          />
        </div>

        <DisciplineSelector
          value={form.disciplines}
          onChange={(next) => updateField("disciplines", next)}
        />
      </form>
    </Modal>
  );
}
