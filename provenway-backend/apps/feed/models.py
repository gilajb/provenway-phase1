# apps/feed has no models of its own. GET /api/v1/feed/ (Engineering Doc
# §5.2) is a read-only query over apps.build_log.ProjectUpdate, scoped to
# the requesting user's follow graph (apps.networking.Follow) and
# filtered through apps.projects.permissions.visible_projects_q — there's
# no new table to back it. This file (and the empty migrations/ package
# next to it) exists so Django treats apps.feed as a normal installed
# app; it deliberately has no migrations to run.
