from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import AuthAuditLog, AuthToken, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ["-created_at"]
    list_display = ["email", "display_name", "subscription_tier", "is_verified", "is_active", "is_staff", "created_at"]
    list_filter = ["subscription_tier", "is_verified", "is_active", "is_staff"]
    search_fields = ["email", "display_name", "phone"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("display_name", "headline", "phone")}),
        ("Status", {"fields": ("is_verified", "is_active", "is_staff", "is_superuser", "subscription_tier")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "display_name", "password1", "password2")}),
    )
    readonly_fields = ["created_at", "updated_at", "last_login"]


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "expires_at", "revoked_at", "created_at"]
    list_filter = ["revoked_at"]
    search_fields = ["user__email"]
    readonly_fields = ["id", "token_hash", "created_at", "updated_at"]


@admin.register(AuthAuditLog)
class AuthAuditLogAdmin(admin.ModelAdmin):
    list_display = ["event_type", "user", "ip_address", "created_at"]
    list_filter = ["event_type"]
    search_fields = ["user__email", "ip_address"]
    readonly_fields = [f.name for f in AuthAuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
