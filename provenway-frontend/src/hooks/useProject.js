/**
 * src/hooks/useProject.js
 * ────────────────────────
 * Fetch a single project (apps/build_log — GET /projects/{id}/) and expose
 * the owner-only mutations the detail page needs:
 *
 *  - updateProject: PATCH /projects/{id}/ (owner only, server-enforced)
 *  - deleteProject: DELETE /projects/{id}/ (soft-delete, owner only)
 *
 * 404 handling: the backend returns 404 (never 403) for both "doesn't
 * exist" and "exists but you can't see it" (private / connections-only /
 * soft-deleted) — see Engineering Doc §6.1 threat model. This hook makes
 * no attempt to distinguish those cases; the page just renders one
 * "not found" state either way, matching the backend's intent not to leak
 * existence of inaccessible resources.
 */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../lib/api/apiClient";
import { PROJECTS } from "../lib/api/endpoints";

export function useProject(projectId) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => apiClient.get(PROJECTS.by_id(projectId)),
    enabled: !!projectId,
    staleTime: 1000 * 30,
    // Don't burn retries on a 404 — it's not going to resolve itself.
    retry: (failureCount, error) => error?.status !== 404 && failureCount < 2,
  });

  const updateProject = useMutation({
    mutationFn: (patch) => apiClient.patch(PROJECTS.by_id(projectId), patch),
    onSuccess: (updated) => {
      queryClient.setQueryData(["project", projectId], (prev) =>
        prev ? { ...prev, ...updated } : updated
      );
    },
  });

  const deleteProject = useMutation({
    mutationFn: () => apiClient.delete(PROJECTS.by_id(projectId)),
    onSuccess: () => {
      queryClient.removeQueries({ queryKey: ["project", projectId] });
      queryClient.removeQueries({ queryKey: ["project-updates", projectId] });
    },
  });

  return { ...query, updateProject, deleteProject };
}

export default useProject;
