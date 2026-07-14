import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Follow(models.Model):
    """follows table (Engineering Doc §3.2.2) — this session covers Follow
    only. `blocks` and `endorsements` (also §3.2.2) are separate future
    sessions and are deliberately not built here.

    Deviation from the doc: §3.2.2 specifies a composite primary key
    (follower_id, following_id). Django 5.0 (pinned in
    requirements/base.txt) has no support for multi-column primary keys
    — that lands in Django 5.2's CompositePrimaryKey — so this uses a
    UUID surrogate PK plus a UniqueConstraint on (follower, following),
    the same pattern already used for apps.projects.ProjectDiscipline.
    The UniqueConstraint gives the same one-row-per-pair guarantee the
    doc's composite PK was there for.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_relations",  # rows where this user is the one doing the following
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower_relations",  # rows where this user is being followed
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "follows"
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow_pair"
            ),
            # DB-level backstop for self-follow prevention. The primary
            # enforcement point is Follow.clean() (called explicitly by
            # the view before create — see apps.networking.views) so a
            # self-follow attempt surfaces as a clean 400, not a raw
            # IntegrityError; this constraint just guarantees the rule
            # holds even if some future code path bypasses clean().
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="follow_no_self_follow",
            ),
        ]
        indexes = [
            # Followers-of / follow-status lookups filter on `following`
            # alone; the unique constraint above already covers the
            # (follower, following) pair lookup used for follow-status
            # and idempotent create/delete.
            models.Index(fields=["following"], name="follow_following_idx"),
        ]

    def __str__(self):
        return f"Follow({self.follower_id} -> {self.following_id})"

    def clean(self):
        if self.follower_id is not None and self.follower_id == self.following_id:
            raise ValidationError("A user cannot follow themselves.")
