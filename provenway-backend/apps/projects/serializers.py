from rest_framework import serializers

from apps.authentication.models import Discipline

from .models import Project, ProjectDiscipline


class ProjectOwnerSummarySerializer(serializers.Serializer):
    """Minimal, read-only snapshot of the owning User.

    Kept as a plain Serializer for the same reason as
    apps.profiles.serializers.ProfileUserSummarySerializer — this app
    doesn't need to reach into authentication's serializer layer for a
    handful of display fields a project card needs.
    """

    id = serializers.UUIDField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)


class ProjectSerializer(serializers.ModelSerializer):
    owner = ProjectOwnerSummarySerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()
    # write_only: `disciplines` isn't a real model field on Project (it's
    # the reverse FK manager from ProjectDiscipline), so letting this
    # field participate in the default to_representation() pass would
    # try to iterate a RelatedManager directly and blow up. Output is
    # built explicitly in to_representation() below instead.
    disciplines = serializers.ListField(
        child=serializers.ChoiceField(choices=Discipline.choices),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "owner",
            "is_owner",
            "title",
            "description",
            "location_text",
            "location_lat",
            "location_lng",
            "status",
            "visibility",
            "start_date",
            "end_date",
            "disciplines",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "is_owner", "created_at", "updated_at"]

    def get_is_owner(self, obj) -> bool:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not request or not user or not user.is_authenticated:
            return False
        return obj.owner_id == user.id

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # disciplines is a related-object set, not a model field, so it
        # has to be materialised explicitly rather than left to the
        # ListField declared above (that field only handles input
        # validation on write).
        data["disciplines"] = list(
            instance.disciplines.values_list("discipline", flat=True)
        )
        return data

    def create(self, validated_data):
        disciplines = validated_data.pop("disciplines", [])
        request = self.context["request"]
        project = Project.objects.create(owner=request.user, **validated_data)
        self._sync_disciplines(project, disciplines)
        return project

    def update(self, instance, validated_data):
        disciplines = validated_data.pop("disciplines", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if disciplines is not None:
            self._sync_disciplines(instance, disciplines)
        return instance

    @staticmethod
    def _sync_disciplines(project, disciplines):
        # Full replace on every write — simplest correct behaviour for a
        # small multi-select list; matches how Profile.disciplines (an
        # ArrayField) behaves on PATCH.
        project.disciplines.all().delete()
        ProjectDiscipline.objects.bulk_create(
            [
                ProjectDiscipline(project=project, discipline=d)
                for d in dict.fromkeys(disciplines)  # de-dupe, keep order
            ]
        )
