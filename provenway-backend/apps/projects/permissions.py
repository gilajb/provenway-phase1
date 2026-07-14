def visible_projects_q(user, *, prefix: str = ""):
    """Q object selecting the projects a given user is allowed to view —
    the queryset-level counterpart to user_can_view_project(), for views
    that need to *filter a list* rather than check one already-fetched
    object (list/search endpoints, and now the feed in apps.feed).
    user_can_view_project can't be run row-by-row inside a QuerySet, so
    this mirrors its exact rule set instead: public always included, the
    user's own projects always included, and connections-only projects
    included only when the owner is a *mutual* connection of `user` — the
    same "mutual-follow = connection" definition from Engineering Doc
    §1.4.1 that user_can_view_project's _is_mutual_connection() uses.
    Keep the two in lockstep if either changes.

    Originally this logic lived inline, duplicated, in
    apps.projects.views.ProjectListCreateView.get_queryset(); it's
    extracted here now that apps.feed needs the identical rule a third
    time, and ProjectListCreateView has been switched to call this
    instead of keeping its own copy.

    `prefix` lets this filter a queryset of some *other* model that has a
    FK to Project — e.g. apps.feed passes prefix="project" to filter
    ProjectUpdate rows by their parent project's visibility
    (Project.objects.filter(...) uses prefix="", the default).
    """
    from django.db.models import Q

    from apps.networking.models import Follow

    from .models import ProjectVisibility

    def field(name: str) -> str:
        return f"{prefix}__{name}" if prefix else name

    # Session 16 permission audit: a deactivated/banned owner
    # (User.is_active=False) is already hidden from PublicProfileView
    # (404) and directory search (excluded entirely), but nothing here
    # enforced the same rule. A banned user's public/connections
    # projects and build-log updates kept showing up in project list,
    # project detail, and the feed of anyone who followed them before
    # the ban - a moderation bypass. AND-wrapping every branch below
    # with owner__is_active=True makes it impossible to add a new
    # branch that forgets the check.
    active_owner = Q(**{field("owner__is_active"): True})

    if user is None or not user.is_authenticated:
        return active_owner & Q(**{field("visibility"): ProjectVisibility.PUBLIC})

    following_ids = set(
        Follow.objects.filter(follower=user).values_list("following_id", flat=True)
    )
    follower_ids = set(
        Follow.objects.filter(following=user).values_list("follower_id", flat=True)
    )
    mutual_ids = following_ids & follower_ids

    visible = Q(**{field("visibility"): ProjectVisibility.PUBLIC}) | Q(
        **{field("owner"): user}
    )
    if mutual_ids:
        visible |= Q(
            **{
                field("visibility"): ProjectVisibility.CONNECTIONS,
                f"{field('owner_id')}__in": mutual_ids,
            }
        )
    return active_owner & visible


def user_can_view_project(project, user):
    """Visibility gate shared by the list and detail endpoints.

    - public: anyone (including anonymous)
    - private: owner only
    - connections: owner, plus mutual connections of the owner (see
      _is_mutual_connection below)
    """
    from .models import ProjectVisibility

    # Session 16 permission audit: mirror the same owner__is_active gate
    # visible_projects_q applies to the list/feed queryset form of this
    # rule (see that function's comment for why). A deactivated/banned
    # owner's project is hidden from everyone, including the owner
    # themself - moot in practice, since a banned user's is_active=False
    # already blocks them from logging in at all (see LoginSerializer),
    # so "owner viewing their own project" can't happen for a banned
    # account regardless.
    if not project.owner.is_active:
        return False

    if project.visibility == ProjectVisibility.PUBLIC:
        return True

    if user is None or not user.is_authenticated:
        return False

    if project.owner_id == user.id:
        return True

    if project.visibility == ProjectVisibility.CONNECTIONS:
        return _is_mutual_connection(project.owner_id, user.id)

    return False  # PRIVATE and anything else not covered above


def _is_mutual_connection(owner_id, viewer_id):
    """Is `viewer_id` a connection of `owner_id`, for `connections`-tier
    project visibility?

    apps.networking's Follow model now exists (this session), so this
    replaces the previous owner-only TODO stub.

    Direction chosen: **mutual follow**, not "viewer follows owner" and
    not "owner follows viewer". The Engineering Doc doesn't spell out
    which direction §2.5 / §3.2.2 mean by "connections only" at the
    point it describes project visibility, but the doc does define the
    term itself in §1.4.1: "Follow / unfollow users; mutual-follow =
    connection." That's the definition used here — a one-directional
    check would mean either a) any account that follows the owner (e.g.
    a cold follow from a recruiter who's never been followed back) can
    see connections-only projects, or b) anyone the owner follows (who
    may not follow back, so may not consider themselves connected at
    all) can see them. Both leak beyond what a reasonable owner would
    expect "connections only" to mean; mutual follow is the one reading
    consistent with the doc's own definition of "connection".

    Two queries + a set intersection rather than a single ORM query with
    a self-join, since Follow doesn't have a natural "are these two
    mutually connected" queryset method yet — fine at this scale, worth
    revisiting (e.g. a single EXISTS-of-EXISTS query) if this becomes a
    hot path.
    """
    from apps.networking.models import Follow

    return (
        Follow.objects.filter(follower_id=owner_id, following_id=viewer_id).exists()
        and Follow.objects.filter(follower_id=viewer_id, following_id=owner_id).exists()
    )
