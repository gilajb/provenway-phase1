/**
 * src/pages/main/VerificationPage.jsx
 * ──────────────────────────────────────
 * Submit a credential document (licence/degree/membership/ID) for admin
 * review, and see the status of past submissions. Approval (via Django
 * admin — no custom review UI this session, matching how apps.leads'
 * InterestSignup queue is also admin-only) sets User.is_verified, which
 * VerifiedBadge (already wired) then reflects everywhere.
 */
import { useRef, useState } from "react";
import { AlertCircle, FileCheck2, ShieldCheck, UploadCloud } from "lucide-react";

import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import { useVerification } from "../../hooks/useVerification";
import { getErrorMessage } from "../../lib/api/errorMessages";
import styles from "./VerificationPage.module.css";

const DOCUMENT_TYPE_OPTIONS = [
  { value: "licence", label: "Professional Licence" },
  { value: "degree", label: "Degree Certificate" },
  { value: "membership", label: "Professional Body Membership" },
  { value: "id", label: "Government ID" },
];

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
const MAX_BYTES = 10 * 1024 * 1024; // 10MB, matches backend cap

const STATUS_BADGE_VARIANT = { pending: "muted", approved: "success", rejected: "default" };
const STATUS_LABEL = { pending: "Pending review", approved: "Verified", rejected: "Rejected" };

function validateFile(file) {
  if (!ACCEPTED_TYPES.includes(file.type)) {
    return "Please choose a PDF, JPG, PNG, or WEBP file.";
  }
  if (file.size > MAX_BYTES) {
    return "File must be smaller than 10MB.";
  }
  return null;
}

export default function VerificationPage() {
  const { data: credentials, isLoading, submitCredential } = useVerification();
  const inputRef = useRef(null);

  const [documentType, setDocumentType] = useState(DOCUMENT_TYPE_OPTIONS[0].value);
  const [file, setFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [formError, setFormError] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  function handleFileChange(e) {
    const selected = e.target.files?.[0];
    e.target.value = "";
    if (!selected) return;

    const validationError = validateFile(selected);
    if (validationError) {
      setFile(null);
      setFileError(validationError);
      return;
    }
    setFileError(null);
    setFile(selected);
  }

  function handleSubmit(e) {
    e.preventDefault();
    setFormError(null);
    setSubmitted(false);
    if (!file) {
      setFileError("Please choose a file to upload.");
      return;
    }

    submitCredential.mutate(
      { documentType, file },
      {
        onSuccess: () => {
          setFile(null);
          setSubmitted(true);
        },
        onError: (err) => setFormError(getErrorMessage(err)),
      }
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.headerIcon}>
          <ShieldCheck size={22} />
        </div>
        <div>
          <h1 className={styles.title}>Get Verified</h1>
          <p className={styles.subtitle}>
            Submit a professional licence, degree, membership, or government ID for review.
            Once approved, a verified badge appears on your profile and build log entries.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className={styles.form}>
        <Select
          label="Document type"
          options={DOCUMENT_TYPE_OPTIONS}
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
        />

        <div className={styles.fileField}>
          <button
            type="button"
            className={styles.filePickerBtn}
            onClick={() => inputRef.current?.click()}
          >
            <UploadCloud size={16} />
            {file ? file.name : "Choose a file (PDF, JPG, PNG, or WEBP)"}
          </button>
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED_TYPES.join(",")}
            className={styles.hiddenInput}
            onChange={handleFileChange}
          />
          {fileError && <p className={styles.fieldError}>{fileError}</p>}
        </div>

        {formError && (
          <div className={styles.errorBanner} role="alert">
            <AlertCircle size={16} />
            <span>{formError}</span>
          </div>
        )}

        {submitted && (
          <div className={styles.successBanner}>
            <FileCheck2 size={16} />
            <span>Submitted — we&apos;ll review it and update the status below.</span>
          </div>
        )}

        <Button type="submit" loading={submitCredential.isPending}>
          Submit for review
        </Button>
      </form>

      <div className={styles.history}>
        <h2 className={styles.historyTitle}>Your submissions</h2>
        {isLoading && <p className={styles.emptyText}>Loading…</p>}
        {!isLoading && (!credentials || credentials.length === 0) && (
          <p className={styles.emptyText}>You haven&apos;t submitted any documents yet.</p>
        )}
        {!isLoading && credentials?.map((credential) => (
          <div key={credential.id} className={styles.historyRow}>
            <div>
              <p className={styles.historyDocType}>
                {DOCUMENT_TYPE_OPTIONS.find((o) => o.value === credential.document_type)?.label ??
                  credential.document_type}
              </p>
              {credential.status === "rejected" && credential.rejection_reason && (
                <p className={styles.rejectionReason}>{credential.rejection_reason}</p>
              )}
            </div>
            <Badge variant={STATUS_BADGE_VARIANT[credential.status]}>
              {STATUS_LABEL[credential.status] ?? credential.status}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
