/**
 * src/hooks/useNotifications.js
 * ─────────────────────────────
 * Fetch notifications and expose mark-read helpers.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../lib/api/apiClient";
import { NOTIFICATIONS } from "../lib/api/endpoints";

export function useNotifications() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["notifications"],
    queryFn: () => apiClient.get(NOTIFICATIONS.LIST),
    refetchInterval: 30_000,
  });

  const markRead = useMutation({
    mutationFn: (id) => apiClient.post(NOTIFICATIONS.read(id), {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  const markAllRead = useMutation({
    mutationFn: () => apiClient.post(NOTIFICATIONS.READ_ALL, {}),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notifications"] }),
  });

  return { ...query, markRead, markAllRead };
}
