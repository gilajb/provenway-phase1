from django.contrib import admin

from .models import InterestSignup


@admin.register(InterestSignup)
class InterestSignupAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "organization_name", "interest_type", "source_page", "created_at"]
    list_filter = ["interest_type"]
    search_fields = ["name", "email", "organization_name"]
    readonly_fields = [f.name for f in InterestSignup._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
