"""provenway/urls.py — root URL configuration.

URL includes are added here only when the corresponding app is fully
scaffolded. Do not add an include() before the app's urls.py exists
and has a urlpatterns list.
"""

from django.contrib import admin
from django.urls import include, path

from apps.build_log.views import ProjectExportStatusView

API_V1 = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{API_V1}auth/", include("apps.authentication.urls")),
    path(f"{API_V1}profiles/", include("apps.profiles.urls")),
    path(f"{API_V1}projects/", include("apps.projects.urls")),
    # ProjectUpdate/UpdatePhoto (build log entries + photos) — nested under
    # the same /projects/ prefix since every route here starts with
    # <uuid:project_id>/updates/. Co-signatures remain a future session
    # (see apps/build_log models.py for what's deliberately out of scope).
    path(f"{API_V1}projects/", include("apps.build_log.urls")),
    # apps.networking (Follow only, this session) is mounted under
    # /users/ rather than /networking/ — the endpoints it defines
    # (follow/unfollow/followers/following/follow-status) are all about
    # a *user* resource, matching how Engineering Doc §5.2 lists them
    # under "Users & Profiles", not under a separate networking prefix.
    path(f"{API_V1}users/", include("apps.networking.urls")),
    # Directory search (GET /api/v1/users/ — Engineering Doc §5.2) is a
    # second include at the same /users/ prefix rather than a route added
    # inside apps.networking.urls: it's profile/search domain logic (query
    # over Profile, not the follow graph), so it lives in apps.profiles.
    # Django tries same-prefix includes in list order and falls through
    # to the next on no match, so this coexists cleanly with the
    # <uuid:user_id>/... patterns above.
    path(f"{API_V1}users/", include("apps.profiles.directory_urls")),
    path(f"{API_V1}feed/", include("apps.feed.urls")),
    # apps.leads — public lead capture for marketing pages whose product
    # area (firms, institutions) has no self-serve account flow yet.
    path(f"{API_V1}leads/", include("apps.leads.urls")),
    # Flat /tasks/{id}/ per Engineering Doc §5.2 — the only async-job
    # producer right now is apps.build_log's PDF export, so this imports
    # that view directly rather than standing up a dedicated tasks app.
    # If a second job producer shows up, promote this to a real
    # apps/tasks app instead of importing across app boundaries again.
    path(f"{API_V1}tasks/<str:task_id>/", ProjectExportStatusView.as_view(), name="task-status"),
    path(f"{API_V1}credentials/", include("apps.verification.urls")),
    # Additional app URLs are uncommented as each app is scaffolded:
    # NOTE: Project CRUD lives in apps.projects; ProjectUpdate/UpdatePhoto
    # now live in apps.build_log (wired in above) as originally planned.
    # apps.feed (GET /feed/ only, this session) is wired in above.
    # path(f"{API_V1}jobs/", include("apps.recruitment.urls")),
    # path(f"{API_V1}tenders/", include("apps.tenders.urls")),
    # path(f"{API_V1}conversations/", include("apps.messaging.urls")),
    # path(f"{API_V1}notifications/", include("apps.notifications.urls")),
    # path(f"{API_V1}organisations/", include("apps.organisations.urls")),
    # path(f"{API_V1}billing/", include("apps.billing.urls")),
    # path(f"{API_V1}search/", include("apps.search.urls")),
    # path(f"{API_V1}admin-api/", include("apps.admin_panel.urls")),
]

if __import__("django.conf", fromlist=["settings"]).settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass
