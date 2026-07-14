/**
 * src/hooks/useProjectUpdates.js
 * ────────────────────────────────
 * Update timeline for a project (apps/build_log):
 *
 *  - GET /projects/{id}/updates/ — paginated (cursor or offset, we don't
 *    assume which: we just follow whatever absolute `next` URL DRF's
 *    pagination class returns, the same defensive approach as useFeed.js)
 *  - createUpdate: POST /projects/{id}/updates/ (owner only)
 *  - addPhoto: POST /projects/{id}/updates/{uid}/photos/ — registers a
 *    photo that has already been uploaded direct-to-Cloudinary (Engineering
 *    Doc §4.2.2: file bytes never pass through Django) with its
 *    cloudinary_public_id, url, and sequence_order
 *
 * New updates/photos are pushed into the first page of the cached list
 * on success so the timeline reflects them immediately without a refetch.
 */
import { useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../lib/api/apiClient";
import { PROJECTS } from "../lib/api/endpoints";

export function useProjectUpdates(projectId) {
  const queryClient = useQueryClient();
  const queryKey = ["project-updates", projectId];

  const query = useInfiniteQuery({
    queryKey,
    queryFn: ({ pageParam }) => apiClient.get(pageParam || PROJECTS.UPDATES(projectId)),
    initialPageParam: null,
    getNextPageParam: (lastPage) => lastPage?.next || undefined,
    enabled: !!projectId,
    staleTime: 1000 * 30,
  });

  const createUpdate = useMutation({
    mutationFn: (payload) => apiClient.post(PROJECTS.UPDATES(projectId), payload),
    onSuccess: (created) => {
      queryClient.setQueryData(queryKey, (data) => {
        if (!data) return data;
        const [first, ...rest] = data.pages;
        const results = [created, ...(first?.results ?? [])];
        return { ...data, pages: [{ ...first, results }, ...rest] };
      });
    },
  });

  const addPhoto = useMutation({
    mutationFn: ({ updateId, photo }) =>
      apiClient.post(PROJECTS.photos(projectId, updateId), photo),
    onSuccess: (savedPhoto, { updateId }) => {
      queryClient.setQueryData(queryKey, (data) => {
        if (!data) return data;
        const pages = data.pages.map((page) => ({
          ...page,
          results: (page.results ?? []).map((u) =>
            u.id === updateId
              ? { ...u, photos: [...(u.photos ?? []), savedPhoto] }
              : u
          ),
        }));
        return { ...data, pages };
      });
    },
  });

  return { ...query, createUpdate, addPhoto };
}

export default useProjectUpdates;
