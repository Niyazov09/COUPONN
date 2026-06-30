from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Project, Task, Comment


# ---------------- PROJECT ----------------

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    members = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username"
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "owner",
            "members",
            "created_at",
        ]

# ---------------- TASK ----------------

class TaskSerializer(serializers.ModelSerializer):
    # WRITE: принимаем username
    assignee = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        project = attrs.get(
            "project",
            getattr(self.instance, "project", None)
        )

        assignee = attrs.get("assignee")

        if assignee and project and not project.is_member(assignee):
            raise serializers.ValidationError({
                "assignee": "Исполнитель должен быть участником проекта."
            })

        return attrs


# ---------------- COMMENT ----------------

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = [
            "id",
            "task",
            "author",
            "text",
            "created_at",
        ]