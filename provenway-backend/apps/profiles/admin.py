from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "firm_name", "years_experience", "location_text", "updated_at"]
    search_fields = ["user__email", "user__display_name", "firm_name", "location_text"]
    list_filter = ["disciplines"]
    readonly_fields = ["id", "created_at", "updated_at"]
