/**
 * src/components/profile/EditProfileModal.jsx
 * ───────────────────────────────────────────────
 * Edit form for the fields apps/profiles owns: bio, disciplines,
 * location, years of experience, and firm name. PATCHes /profiles/me/
 * via the updateProfile mutation passed in from useProfile().
 */
import { useEffect, useState } from "react";
import { AlertCircle } from "lucide-react";

import Modal from "../ui/Modal";
import Input from "../ui/Input";
import Textarea from "../ui/Textarea";
import Button from "../ui/Button";
import DisciplineSelector from "./DisciplineSelector";
import { getErrorMessage, getFieldErrors } from "../../lib/api/errorMessages";
import styles from "./EditProfileModal.module.css";

const BIO_MAX_LENGTH = 500;

function buildInitialForm(profile) {
  return {
    bio: profile?.bio ?? "",
    disciplines: profile?.disciplines ?? [],
    location_text: profile?.location_text ?? "",
    years_of_experience: profile?.years_of_experience ?? "",
    firm_name: profile?.firm_name ?? "",
  };
}

export default function EditProfileModal({ isOpen, onClose, profile, updateProfile }) {
  const [form, setForm] = useState(() => buildInitialForm(profile));
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);

  // Reset the form to the latest saved profile every time the modal opens.
  useEffect(() => {
    if (isOpen) {
      setForm(buildInitialForm(profile));
      setFieldErrors({});
      setFormError(null);
    }
  }, [isOpen, profile]);

  function updateField(field, val) {
    setForm((f) => ({ ...f, [field]: val }));
    if (fieldErrors[field]) setFieldErrors((f) => ({ ...f, [field]: null }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError(null);

    const patch = {
      bio: form.bio.trim(),
      disciplines: form.disciplines,
      location_text: form.location_text.trim(),
      firm_name: form.firm_name.trim(),
      years_of_experience:
        form.years_of_experience === "" ? null : Number(form.years_of_experience),
    };

    try {
      await updateProfile.mutateAsync(patch);
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
      title="Edit profile"
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={updateProfile.isPending}>
            Cancel
          </Button>
          <Button type="submit" form="edit-profile-form" loading={updateProfile.isPending}>
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

      <form id="edit-profile-form" onSubmit={handleSubmit} className={styles.form} noValidate>
        <Textarea
          label="Bio"
          value={form.bio}
          maxLength={BIO_MAX_LENGTH}
          rows={4}
          error={fieldErrors.bio}
          placeholder="Tell other professionals about your work…"
          onChange={(e) => updateField("bio", e.target.value)}
        />

        <DisciplineSelector
          value={form.disciplines}
          onChange={(next) => updateField("disciplines", next)}
        />

        <Input
          label="Location"
          value={form.location_text}
          error={fieldErrors.location_text}
          placeholder="e.g. Nairobi, Kenya"
          onChange={(e) => updateField("location_text", e.target.value)}
        />

        <div className={styles.row}>
          <Input
            label="Years of experience"
            type="number"
            min={0}
            max={80}
            value={form.years_of_experience}
            error={fieldErrors.years_of_experience}
            onChange={(e) => updateField("years_of_experience", e.target.value)}
          />

          <Input
            label="Firm / company"
            value={form.firm_name}
            error={fieldErrors.firm_name}
            placeholder="e.g. Global Infra Partners"
            onChange={(e) => updateField("firm_name", e.target.value)}
          />
        </div>
      </form>
    </Modal>
  );
}
