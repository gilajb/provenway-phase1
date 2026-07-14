from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner_id = getattr(obj, "owner_id", None)
        if owner_id is None:
            owner = getattr(obj, "owner", None)
            owner_id = getattr(owner, "id", None)
        return owner_id == getattr(request.user, "id", None)


class IsVerifiedUser(permissions.BasePermission):
    message = "Only verified professionals can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_verified", False)
        )


class IsProfessionalTier(permissions.BasePermission):
    message = "This feature requires a Professional or Pro+ subscription."
    allowed_tiers = {"professional", "pro_plus"}

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "subscription_tier", None) in self.allowed_tiers
        )


class IsFirmTier(permissions.BasePermission):
    message = "This feature requires a Firm subscription."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "subscription_tier", None) == "firm"
        )
