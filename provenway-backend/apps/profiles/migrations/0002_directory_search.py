import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.conf import settings
from django.db import migrations, models

# Raw SQL, not the ORM: this UPDATE spans profiles + users (search_vector
# combines Profile's own fields with User.display_name/headline), and
# Django's QuerySet.update() forbids joined-field references on the
# right-hand side of a SET clause. Kept in sync with the identical
# per-row statement in apps.profiles.search.update_search_vector — this
# one just omits the `AND profiles.id = ...` filter to backfill every
# existing row in one statement.
_BACKFILL_SQL = """
    UPDATE profiles
    SET search_vector =
        setweight(to_tsvector('english', coalesce(u.display_name, '')), 'A')
        || setweight(to_tsvector('english', coalesce(u.headline, '')), 'B')
        || setweight(to_tsvector('english', coalesce(profiles.firm_name, '')), 'B')
        || setweight(to_tsvector('english', coalesce(profiles.bio, '')), 'C')
        || setweight(to_tsvector('english', coalesce(profiles.location_text, '')), 'D')
    FROM users u
    WHERE u.id = profiles.user_id
"""


def backfill_search_vector(apps, schema_editor):
    schema_editor.execute(_BACKFILL_SQL)


def noop_reverse(apps, schema_editor):
    # Nothing to undo — reversing AddField below already drops the column.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                blank=True, editable=False, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="profile",
            # Recreates the geographic composite index the schema had on
            # users.location_lat/location_lng (Engineering Doc §3.2.1)
            # before those columns moved to Profile — dropped in
            # authentication/migrations/0004 and never re-added until now.
            index=models.Index(
                fields=["location_lat", "location_lng"], name="profiles_location_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="profile",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="profiles_search_vector_gin"
            ),
        ),
        migrations.RunPython(backfill_search_vector, noop_reverse),
    ]
