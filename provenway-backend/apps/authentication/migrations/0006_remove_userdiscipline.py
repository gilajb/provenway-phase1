from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0005_migrate_userdiscipline_to_profile"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="userdiscipline",
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name="userdiscipline",
            name="user",
        ),
        migrations.DeleteModel(
            name="UserDiscipline",
        ),
    ]
