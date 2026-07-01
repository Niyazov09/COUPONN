from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Project, Task, Comment
from .serializers import ProjectSerializer, TaskSerializer, CommentSerializer
from .permissions import (
    IsProjectOwner,
    IsTaskProjectMember,
    IsCommentProjectMember,
    IsProjectOwnerOrMember,
)


# ---------------- PROJECT ----------------

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrMember]

    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsAuthenticated, IsProjectOwner]
        else:
            permission_classes = [IsAuthenticated, IsProjectOwnerOrMember]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        project = self.get_object()

        if project.owner != request.user:
            raise PermissionDenied(
                "Только владелец проекта может добавлять участников."
            )

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = int(user_id)
            user = User.objects.get(pk=user_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "user_id must be integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if project.members.filter(id=user.id).exists():
            return Response({"status": "already member"})

        project.members.add(user)
        return Response({"status": "member added"})


# ---------------- TASK ----------------

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskProjectMember]

    http_method_names = ["get", "post", "patch"]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = ["project", "status", "assignee"]
    search_fields = ["title"]

    ordering_fields = ["priority_weight", "created_at"]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(project__owner=user) |
            Q(project__members=user)
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]

        if not project.is_member(self.request.user):
            raise PermissionDenied("Вы не являетесь участником проекта.")

        serializer.save()

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        task = self.get_object()
        serializer = CommentSerializer(task.comments.all(), many=True)
        return Response(serializer.data)


# ---------------- COMMENT ----------------

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentProjectMember]

    http_method_names = ["get", "post"]

    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(
            Q(task__project__owner=user) |
            Q(task__project__members=user)
        ).distinct()

    def perform_create(self, serializer):
        task = serializer.validated_data["task"]

        if not task.project.is_member(self.request.user):
            raise PermissionDenied("Вы не являетесь участником проекта.")

        serializer.save(author=self.request.user)