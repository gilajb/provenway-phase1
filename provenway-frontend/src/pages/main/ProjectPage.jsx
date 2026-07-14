/**
 * src/pages/main/ProjectPage.jsx
 * ──────────────────────────────
 * Project detail page: header, owner-only edit/delete/add-update
 * controls, project overview, and the build-log update timeline.
 * Backed by apps/build_log (GET/PATCH/DELETE /projects/{id}/,
 * GET/POST /projects/{id}/updates/, POST .../updates/{uid}/photos/).
 *
 * Ownership detection mirrors ProfilePage.jsx's pattern exactly:
 * prefer a server-provided boolean, fall back to comparing the
 * logged-in user's id against the resource. The exact field name the
 * ProjectSerializer uses for this wasn't available while building this,
 * so — like ProfilePage — the check is defensive across a couple of
 * likely shapes (is_owner / is_own_project / owner_id / owner.id).
 *
 * Scope note: the design reference (screen.png / code.html) also shows
 * a project team roster, live progress/incident metrics, and a photo
 * gallery separate from the update timeline. None of that is backed by
 * the Project or ProjectUpdate models (Engineering Doc §3.2.3) — there's
 * no team/org linkage on projects and no standalone gallery endpoint —
 * so rather than inventing data, those sections are a single
 * clearly-labelled "coming soon" panel, same approach ProfilePage.jsx
 * already established for apps/networking's deferred features.
 */
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { FileSearch, Pencil, Plus, Trash2, Users } from "lucide-react";

import { useAuth } from "../../hooks/useAuth";
import { useProject } from "../../hooks/useProject";
import { useProjectUpdates } from "../../hooks/useProjectUpdates";
import { getErrorMessage } from "../../lib/api/errorMessages";

import Button from "../../components/ui/Button";
import ConfirmModal from "../../components/ui/ConfirmModal";
import ComingSoonCard from "../../components/profile/ComingSoonCard";
import ProjectHero from "../../components/project/ProjectHero";
import ProjectOverviewCard from "../../components/project/ProjectOverviewCard";
import UpdateTimeline from "../../components/project/UpdateTimeline";
import EditProjectModal from "../../components/project/EditProjectModal";
import AddUpdateModal from "../../components/project/AddUpdateModal";

import styles from "./ProjectPage.module.css";

function detectOwnership(project, currentUser) {
  if (!project || !currentUser) return false;
  if (typeof project.is_owner === "boolean") return project.is_owner;
  if (typeof project.is_own_project === "boolean") return project.is_own_project;
  if (project.owner_id) return currentUser.id === project.owner_id;
  if (project.owner?.id) return currentUser.id === project.owner.id;
  return false;
}

export default function ProjectPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();

  const { data: project, isLoading, isError, error, updateProject, deleteProject } =
    useProject(id);
  const updatesQuery = useProjectUpdates(id);

  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isAddUpdateOpen, setIsAddUpdateOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  if (isLoading) {
    return <ProjectSkeleton />;
  }

  if (isError) {
    const isNotFound = error?.status === 404;
    return (
      <div className={styles.errorState} role="alert">
        <FileSearch size={28} />
        <h1 className={styles.errorTitle}>
          {isNotFound ? "Project not found" : "Something went wrong"}
        </h1>
        <p className={styles.errorBody}>
          {isNotFound
            ? "This project doesn't exist, or it's private and you don't have access to it."
            : getErrorMessage(error)}
        </p>
        <Button variant="secondary" size="sm" onClick={() => navigate("/feed")}>
          Back to feed
        </Button>
      </div>
    );
  }

  if (!project) return null;

  const isOwner = detectOwnership(project, currentUser);

  async function handleDelete() {
    try {
      await deleteProject.mutateAsync();
      navigate("/feed");
    } catch {
      // ConfirmModal stays open; deleteProject.isError can be surfaced there if needed.
    }
  }

  return (
    <div className={styles.page}>
      <ProjectHero project={project} isOwner={isOwner} />

      {isOwner && (
        <div className={styles.toolbar}>
          <Button variant="secondary" size="sm" onClick={() => setIsAddUpdateOpen(true)}>
            <Plus size={14} />
            Add update
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setIsEditOpen(true)}>
            <Pencil size={14} />
            Edit project
          </Button>
          <Button variant="ghost" size="sm" onClick={() => setIsDeleteOpen(true)}>
            <Trash2 size={14} />
            Delete
          </Button>
        </div>
      )}

      <div className={styles.grid}>
        <main className={styles.main}>
          <ProjectOverviewCard project={project} />

          <section className={styles.card}>
            <h2 className={styles.sectionHeading}>Build Log Timeline</h2>
            <UpdateTimeline
              pages={updatesQuery.data?.pages}
              isLoading={updatesQuery.isLoading}
              isError={updatesQuery.isError}
              error={updatesQuery.error}
              hasNextPage={updatesQuery.hasNextPage}
              isFetchingNextPage={updatesQuery.isFetchingNextPage}
              onLoadMore={() => updatesQuery.fetchNextPage()}
              isOwner={isOwner}
            />
          </section>
        </main>

        <aside className={styles.sidebar}>
          <ComingSoonCard
            icon={Users}
            title="Team & Co-signatures"
            description="Peer co-signatures and project team rosters are coming soon."
          />
        </aside>
      </div>

      {isOwner && (
        <>
          <EditProjectModal
            isOpen={isEditOpen}
            onClose={() => setIsEditOpen(false)}
            project={project}
            updateProject={updateProject}
          />
          <AddUpdateModal
            isOpen={isAddUpdateOpen}
            onClose={() => setIsAddUpdateOpen(false)}
            createUpdate={updatesQuery.createUpdate}
            addPhoto={updatesQuery.addPhoto}
          />
          <ConfirmModal
            isOpen={isDeleteOpen}
            onClose={() => setIsDeleteOpen(false)}
            onConfirm={handleDelete}
            title="Delete this project?"
            description={`"${project.title}" and its entire build log will be removed from your profile. This can't be undone.`}
            confirmLabel="Delete project"
            isLoading={deleteProject.isPending}
          />
        </>
      )}
    </div>
  );
}

function ProjectSkeleton() {
  return (
    <div className={styles.page}>
      <div className={`${styles.skeleton} ${styles.skeletonHero}`} />
      <div className={styles.grid}>
        <main className={styles.main}>
          <div className={`${styles.card} ${styles.skeletonCard}`}>
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "30%" }} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "90%" }} />
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "70%" }} />
          </div>
          <div className={`${styles.card} ${styles.skeletonCard}`}>
            <div className={`${styles.skeleton} ${styles.skeletonLine}`} style={{ width: "40%" }} />
            <div className={`${styles.skeleton} ${styles.skeletonBlock}`} />
          </div>
        </main>
      </div>
    </div>
  );
}
