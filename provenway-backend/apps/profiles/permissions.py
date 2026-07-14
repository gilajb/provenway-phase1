from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """Object-level check for Profile: only the linked User may write.

    core.permissions.IsOwnerOrReadOnly assumes an `owner`/`owner_id`
    attribute (matches Project, Job, Tender etc. per the Engineering Doc).
    Profile's ownership is expressed via `user`/`user_id` instead, so this
    is a small variant rather than forcing Profile to carry a redundant
    `owner_id` alias.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and obj.user_id == request.user.id
        )
