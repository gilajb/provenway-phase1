/**
 * src/components/profile/AvatarUpload.jsx
 * ───────────────────────────────────────────
 * Wraps the shared <Avatar> with an edit affordance for the profile
 * owner. Validates file type/size client-side to match the backend
 * (apps/profiles/.../avatar/ — jpg/png/webp, 5MB cap) before uploading,
 * and shows a local preview + spinner while the upload is in flight.
 */
import { useRef, useState } from "react";
import { Camera, Loader2 } from "lucide-react";

import Avatar from "../ui/Avatar";
import styles from "./AvatarUpload.module.css";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 5 * 1024 * 1024; // 5MB, matches backend cap

function validateFile(file) {
  if (!ACCEPTED_TYPES.includes(file.type)) {
    return "Please choose a JPG, PNG, or WEBP image.";
  }
  if (file.size > MAX_BYTES) {
    return "Image must be smaller than 5MB.";
  }
  return null;
}

export default function AvatarUpload({ src, name, size = 120, editable = false, uploadAvatar }) {
  const inputRef = useRef(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [error, setError] = useState(null);

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow re-selecting the same file later
    if (!file) return;

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    const localPreview = URL.createObjectURL(file);
    setPreviewUrl(localPreview);

    uploadAvatar.mutate(file, {
      onSettled: () => URL.revokeObjectURL(localPreview),
      onSuccess: () => setPreviewUrl(null),
      onError: () => {
        setPreviewUrl(null);
        setError("Upload failed. Please try again.");
      },
    });
  }

  return (
    <div className={styles.wrapper}>
      <Avatar src={previewUrl ?? src} name={name} size={size} />

      {editable && (
        <>
          <button
            type="button"
            className={styles.editBtn}
            onClick={() => inputRef.current?.click()}
            disabled={uploadAvatar.isPending}
            aria-label="Change profile photo"
          >
            {uploadAvatar.isPending ? (
              <Loader2 size={16} className={styles.spin} />
            ) : (
              <Camera size={16} />
            )}
          </button>
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className={styles.hiddenInput}
            onChange={handleFileChange}
          />
        </>
      )}

      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
}
