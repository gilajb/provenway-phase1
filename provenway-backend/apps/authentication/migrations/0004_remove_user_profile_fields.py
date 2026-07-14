from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0003_migrate_profile_fields_to_profile"),
    ]

    operations = [
        # The composite index covered location_lat/location_lng, both of
        # which are being removed below — drop the index first.
        migrations.RemoveIndex(
            model_name="user",
            name="users_locatio_5e7ece_idx",
        ),
        migrations.RemoveField(
            model_name="user",
            name="bio",
        ),
        migrations.RemoveField(
            model_name="user",
            name="location_text",
        ),
        migrations.RemoveField(
            model_name="user",
            name="location_lat",
        ),
        migrations.RemoveField(
            model_name="user",
            name="location_lng",
        ),
        migrations.RemoveField(
            model_name="user",
            name="avatar_url",
        ),
    ]
