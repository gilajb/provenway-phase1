/**
 * src/hooks/useProjectExport.js
 * ───────────────────────────────
 * Kicks off a project's PDF portfolio export (POST /projects/{id}/
 * export-pdf/ → {task_id}) and polls its status (GET /tasks/{task_id}/)
 * until it completes or fails. Polling pattern matches useNotifications.js's
 * refetchInterval precedent, but conditional — stops once the job reaches
 * a terminal state rather than polling forever.
 */
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { apiClient } from "../lib/api/apiClient";
import { PROJECTS, TASKS } from "../lib/api/endpoints";

const TERMINAL_STATUSES = ["completed", "failed"];

export function useProjectExport(projectId) {
  const [taskId, setTaskId] = useState(null);

  const startExport = useMutation({
    mutationFn: () => apiClient.post(PROJECTS.export_pdf(projectId)),
    onSuccess: (data) => setTaskId(data.task_id),
  });

  const statusQuery = useQuery({
    queryKey: ["project-export-status", taskId],
    queryFn: () => apiClient.get(TASKS.by_id(taskId)),
    enabled: !!taskId,
    refetchInterval: (query) =>
      TERMINAL_STATUSES.includes(query.state.data?.status) ? false : 3000,
  });

  return {
    startExport: () => startExport.mutate(),
    isStarting: startExport.isPending,
    startError: startExport.error,
    status: statusQuery.data?.status ?? null,
    pdfUrl: statusQuery.data?.pdf_url ?? null,
    error: statusQuery.data?.error ?? null,
  };
}

export default useProjectExport;
