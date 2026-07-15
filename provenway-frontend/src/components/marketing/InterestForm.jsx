/**
 * src/components/marketing/InterestForm.jsx
 * ─────────────────────────────────────────────
 * Lead-capture form for the "For Construction Firms" and "Educational
 * Access" pages — those product areas have no self-serve account flow
 * yet (apps.organisations/billing/recruitment/verification are all
 * empty backend stubs), so instead of pointing at /register (which
 * would only create an unrelated individual account), this posts to
 * POST /leads/interest/ and stores the signup for manual follow-up.
 *
 * Form-handling pattern matches src/pages/auth/Register.jsx: local
 * useState for form/fieldErrors/formError/loading, same validation and
 * error-message helpers, same submitted-state swap on success.
 */
import { useState } from "react";
import { AlertCircle, CheckCircle2 } from "lucide-react";
import Input from "../ui/Input";
import Textarea from "../ui/Textarea";
import Button from "../ui/Button";
import { apiClient } from "../../lib/api/apiClient";
import { LEADS } from "../../lib/api/endpoints";
import { getErrorMessage, getFieldErrors } from "../../lib/api/errorMessages";
import { validateRequired, validateEmail } from "../../utils/validation";
import styles from "./InterestForm.module.css";

const INITIAL_FORM = { name: "", email: "", organization_name: "", message: "", website: "" };

export default function InterestForm({ interestType, sourcePage, submitLabel = "Request Early Access" }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [fieldErrors, setFieldErrors] = useState({});
  const [formError, setFormError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  function updateField(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
    if (fieldErrors[field]) setFieldErrors((f) => ({ ...f, [field]: null }));
  }

  function validate() {
    const errors = {
      name: validateRequired(form.name, "Name"),
      email: validateEmail(form.email),
    };
    setFieldErrors(errors);
    return !Object.values(errors).some(Boolean);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError(null);
    if (!validate()) return;

    setLoading(true);
    try {
      await apiClient.post(LEADS.INTEREST, {
        name: form.name.trim(),
        email: form.email.trim(),
        organization_name: form.organization_name.trim(),
        interest_type: interestType,
        message: form.message.trim(),
        source_page: sourcePage,
        website: form.website,
      });
      setSubmitted(true);
    } catch (err) {
      setFieldErrors((f) => ({ ...f, ...getFieldErrors(err) }));
      setFormError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <div className={styles.successState}>
        <div className={styles.successIcon}>
          <CheckCircle2 size={26} />
        </div>
        <h3 className={styles.successTitle}>Thanks — we&apos;ll be in touch</h3>
        <p className={styles.successText}>
          We&apos;ve noted your interest and will reach out when this launches.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form} noValidate>
      {formError && (
        <div className={styles.errorBanner} role="alert">
          <AlertCircle size={16} />
          <span>{formError}</span>
        </div>
      )}

      <Input
        label="Full name"
        autoComplete="name"
        value={form.name}
        error={fieldErrors.name}
        onChange={(e) => updateField("name", e.target.value)}
      />

      <Input
        label="Email"
        type="email"
        autoComplete="email"
        value={form.email}
        error={fieldErrors.email}
        onChange={(e) => updateField("email", e.target.value)}
      />

      <Input
        label="Organization (optional)"
        autoComplete="organization"
        value={form.organization_name}
        error={fieldErrors.organization_name}
        onChange={(e) => updateField("organization_name", e.target.value)}
      />

      <Textarea
        label="Anything we should know? (optional)"
        rows={3}
        value={form.message}
        error={fieldErrors.message}
        onChange={(e) => updateField("message", e.target.value)}
      />

      {/* Honeypot — hidden from real visitors via CSS, never via type="hidden"
          (bots specifically skip type="hidden" fields). Left unstyled here
          on purpose; visibility is handled entirely in InterestForm.module.css. */}
      <div className={styles.honeypotField} aria-hidden="true">
        <label htmlFor="website">Website</label>
        <input
          id="website"
          name="website"
          type="text"
          tabIndex={-1}
          autoComplete="off"
          value={form.website}
          onChange={(e) => updateField("website", e.target.value)}
        />
      </div>

      <Button type="submit" fullWidth loading={loading}>
        {submitLabel}
      </Button>
    </form>
  );
}
