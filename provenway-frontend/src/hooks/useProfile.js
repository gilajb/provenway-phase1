/**
 * src/hooks/useProfile.js
 * ───────────────────────
 * Fetch a user profile by ID (apps/profiles — the single source of truth
 * for bio, location, avatar_url, and disciplines) and expose the two
 * mutations a profile page needs:
 *
 *  - updateProfile: PATCH /profiles/me/ (bio, disciplines, location_text,
 *    years_of_experience, firm_name — server enforces the field whitelist)
 *  - uploadAvatar: POST /profiles/me/avatar/ (multipart, server-mediated —
 *    file bytes go to Django, which validates + forwards to Cloudinary)
 *
 * Both mutations only ever target the current user's own profile, but
 * they're exposed from useProfile(userId) so a profile page can call
 * everything from one hook and have the cache kept in sync automatically.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../lib/api/apiClient";
import { PROFILES } from "../lib/api/endpoints";

export function useProfile(userId) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["profile", userId],
    queryFn: () => apiClient.get(PROFILES.by_id(userId)),
    enabled: !!userId,
    staleTime: 1000 * 60 * 5,
  });

  const updateProfile = useMutation({
    mutationFn: (patch) => apiClient.patch(PROFILES.ME, patch),
    onSuccess: (updated) => {
      queryClient.setQueryData(["profile", userId], (prev) =>
        prev ? { ...prev, ...updated } : updated
      );
    },
  });

  const uploadAvatar = useMutation({
    mutationFn: (file) => {
      const formData = new FormData();
      formData.append("avatar", file);
      // Let the browser set multipart/form-data + boundary itself — the
      // apiClient instance defaults Content-Type to application/json,
      // which would otherwise stomp on the boundary param.
      return apiClient.post(PROFILES.AVATAR, formData, {
        headers: { "Content-Type": undefined },
      });
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["profile", userId], (prev) =>
        prev ? { ...prev, avatar_url: updated?.avatar_url ?? prev.avatar_url } : prev
      );
    },
  });

  return { ...query, updateProfile, uploadAvatar };
}

export default useProfile;
