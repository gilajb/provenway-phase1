from rest_framework import permissions


class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """Only the parent Project's owner may write to a ProjectUpdate.

    Distinct from core.permissions.IsOwnerOrReadOnly, which compares
    obj.owner_id directly — ProjectUpdate has no `owner` field of its own
    (only `author`), and per Engineering Doc §5.2 the create/edit/delete
    actions on Build Log updates are gated on the *project's* owner, not
    on whoever is logged in as the entry's author.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and obj.project.owner_id == request.user.id
        )
