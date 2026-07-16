/**
 * src/hooks/useVerification.js
 * ───────────────────────────────
 * List the current user's credential submissions (GET /credentials/me/)
 * and submit a new one (POST /credentials/). Upload is server-mediated
 * multipart, same FormData + Content-Type-override pattern as
 * useProfile.js's uploadAvatar mutation.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../lib/api/apiClient";
import { CREDENTIALS } from "../lib/api/endpoints";

export function useVerification() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["credentials-me"],
    queryFn: () => apiClient.get(CREDENTIALS.ME),
  });

  const submitCredential = useMutation({
    mutationFn: ({ documentType, file }) => {
      const formData = new FormData();
      formData.append("document_type", documentType);
      formData.append("document", file);
      return apiClient.post(CREDENTIALS.LIST, formData, {
        headers: { "Content-Type": undefined },
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["credentials-me"] }),
  });

  return { ...query, submitCredential };
}

export default useVerification;
