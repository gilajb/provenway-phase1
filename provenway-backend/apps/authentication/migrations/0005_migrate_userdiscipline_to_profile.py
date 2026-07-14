from django.db import migrations


def copy_userdiscipline_to_profile(apps, schema_editor):
    UserDiscipline = apps.get_model("authentication", "UserDiscipline")
    Profile = apps.get_model("profiles", "Profile")

    # Group existing rows by user first so each Profile is only written
    # once, even if a user has several UserDiscipline rows.
    disciplines_by_user = {}
    for row in UserDiscipline.objects.all().iterator():
        disciplines_by_user.setdefault(row.user_id, set()).add(row.discipline)

    for user_id, discipline_set in disciplines_by_user.items():
        profile, _ = Profile.objects.get_or_create(user_id=user_id)
        merged = set(profile.disciplines or []) | discipline_set
        if merged != set(profile.disciplines or []):
            profile.disciplines = sorted(merged)
            profile.save(update_fields=["disciplines"])


def copy_profile_disciplines_back_to_userdiscipline(apps, schema_editor):
    # Best-effort reverse: recreate UserDiscipline rows from Profile.disciplines.
    UserDiscipline = apps.get_model("authentication", "UserDiscipline")
    Profile = apps.get_model("profiles", "Profile")

    for profile in Profile.objects.all().iterator():
        for discipline in profile.disciplines or []:
            UserDiscipline.objects.get_or_create(user_id=profile.user_id, discipline=discipline)


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0004_remove_user_profile_fields"),
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            copy_userdiscipline_to_profile,
            reverse_code=copy_profile_disciplines_back_to_userdiscipline,
        ),
    ]
