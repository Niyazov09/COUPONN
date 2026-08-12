from rest_framework import serializers

from ..models import Comment, Project, Task


# ---------------- PROJECT ----------------

class ProjectCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)


class ProjectUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)


class ProjectAddMemberSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


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
        read_only_fields = fields


# ---------------- TASK ----------------

class TaskCreateSerializer(serializers.Serializer):
    project = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES, default="todo")
    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICES, default="medium")
    assignee = serializers.IntegerField(required=False, allow_null=True, default=None)


class TaskUpdateSerializer(serializers.Serializer):
    # Поле объявлено, чтобы попытка сменить проект дошла до сервиса и
    # была отклонена там (Ф-5) — форма данных валидна, а бизнес-правило
    # проверяет сервис.
    project = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=200, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES, required=False)
    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICES, required=False)
    assignee = serializers.IntegerField(required=False, allow_null=True)


class TaskSerializer(serializers.ModelSerializer):
    assignee_username = serializers.CharField(
        source="assignee.username",
        read_only=True,
        default=None,
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
            "assignee_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


# ---------------- COMMENT ----------------

class CommentCreateSerializer(serializers.Serializer):
    task = serializers.IntegerField()
    text = serializers.CharField()


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
        read_only_fields = fields
