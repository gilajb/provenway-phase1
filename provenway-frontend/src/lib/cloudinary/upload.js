/**
 * src/lib/cloudinary/upload.js
 * ────────────────────────────
 * Direct-to-Cloudinary file upload.
 * File bytes NEVER pass through Django (Engineering Doc §4.2.2).
 */

const CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME;
const UPLOAD_PRESET = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET;
const UPLOAD_URL = `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`;

export function uploadToCloudinary(file, { onProgress, folder = "provenway/updates" } = {}) {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("upload_preset", UPLOAD_PRESET);
    formData.append("folder", folder);
    formData.append("transformation", "c_limit,w_1200,q_80,f_jpg");

    const xhr = new XMLHttpRequest();

    if (onProgress) {
      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100));
      });
    }

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText));
      else reject(new Error(`Cloudinary upload failed: ${xhr.status}`));
    });

    xhr.addEventListener("error", () => reject(new Error("Upload network error")));
    xhr.addEventListener("abort", () => reject(new Error("Upload aborted")));

    xhr.open("POST", UPLOAD_URL);
    xhr.send(formData);
  });
}

export async function uploadMultipleToCloudinary(files, options = {}) {
  const capped = files.slice(0, 10); // Max 10 photos per update
  return Promise.all(capped.map((file) => uploadToCloudinary(file, options)));
}

export function cloudinaryUrl(publicId, transforms = {}) {
  if (!publicId) return "";
  const parts = Object.entries(transforms).map(([k, v]) => `${k[0]}_${v}`).join(",");
  const t = parts ? `${parts}/` : "";
  return `https://res.cloudinary.com/${CLOUD_NAME}/image/upload/${t}${publicId}`;
}

export const avatarUrl = (publicId, size = 80) =>
  cloudinaryUrl(publicId, { w: size, h: size, c: "fill", g: "face", q: "auto", f: "auto" });

export const photoCardUrl = (publicId) =>
  cloudinaryUrl(publicId, { w: 600, q: "auto", f: "auto" });
