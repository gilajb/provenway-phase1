from django.db import migrations

# Fields being retired from User in favour of the single source of truth on
# apps.profiles.Profile (Profile already carries all of these — see
# apps/profiles/models.py). Only copied when the User-side value is
# non-null/non-blank, and only into a Profile field that is still
# empty, so this never clobbers real data a user may have already entered
# through the Profile API (/profiles/me/) since that app was wired up.
FIELDS_TO_MIGRATE = ["bio", "location_text", "location_lat", "location_lng", "avatar_url"]


def copy_user_fields_to_profile(apps, schema_editor):
    User = apps.get_model("authentication", "User")
    Profile = apps.get_model("profiles", "Profile")

    users_with_data = User.objects.exclude(
        bio__isnull=True, location_text__isnull=True,
        location_lat__isnull=True, location_lng__isnull=True,
        avatar_url__isnull=True,
    ).exclude(
        bio="", location_text="", avatar_url="",
    )

    for user in users_with_data.iterator():
        profile, _ = Profile.objects.get_or_create(user_id=user.pk)
        changed_fields = []
        for field in FIELDS_TO_MIGRATE:
            user_value = getattr(user, field)
            if user_value in (None, ""):
                continue
            profile_value = getattr(profile, field)
            if profile_value in (None, ""):
                setattr(profile, field, user_value)
                changed_fields.append(field)
        if changed_fields:
            profile.save(update_fields=changed_fields)


def copy_profile_fields_back_to_user(apps, schema_editor):
    # Reverse: best-effort restore, so `migrate authentication 0002` stays
    # usable during development. Only fills User fields that are still
    # blank, mirroring the forward direction's non-destructive behaviour.
    User = apps.get_model("authentication", "User")
    Profile = apps.get_model("profiles", "Profile")

    for profile in Profile.objects.select_related("user").iterator():
        user = profile.user
        changed_fields = []
        for field in FIELDS_TO_MIGRATE:
            profile_value = getattr(profile, field)
            if profile_value in (None, ""):
                continue
            user_value = getattr(user, field)
            if user_value in (None, ""):
                setattr(user, field, profile_value)
                changed_fields.append(field)
        if changed_fields:
            user.save(update_fields=changed_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0002_user_is_email_verified"),
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            copy_user_fields_to_profile,
            reverse_code=copy_profile_fields_back_to_user,
        ),
    ]
