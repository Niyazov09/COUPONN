from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .. import selectors, services
from .serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    ProjectAddMemberSerializer,
    ProjectCreateSerializer,
    ProjectSerializer,
    ProjectUpdateSerializer,
    TaskCreateSerializer,
    TaskSerializer,
    TaskUpdateSerializer,
)


class MappedOrderingFilter(OrderingFilter):
    """Позволяет сортировать ?ordering=priority семантически (§8 руководства)."""

    mapping = {"priority": "priority_order", "-priority": "-priority_order"}

    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view) or []
        return [self.mapping.get(field, field) for field in ordering]


# ---------------- PROJECT ----------------

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return selectors.project_list(user=self.request.user)

    def create(self, request):
        s = ProjectCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        project = services.project_create(
            owner=request.user,
            name=s.validated_data["name"],
        )
        return Response(ProjectSerializer(project).data, status=201)

    def partial_update(self, request, pk=None):
        s = ProjectUpdateSerializer(data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        project = services.project_update(
            actor=request.user,
            project_id=pk,
            name=s.validated_data["name"],
        )
        return Response(ProjectSerializer(project).data)

    def destroy(self, request, pk=None):
        services.project_delete(actor=request.user, project_id=pk)
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        s = ProjectAddMemberSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        project = services.project_add_member(
            actor=request.user,
            project_id=pk,
            user_id=s.validated_data["user_id"],
        )
        return Response(ProjectSerializer(project).data)


# ---------------- TASK ----------------

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    http_method_names = ["get", "post", "patch", "delete"]

    filter_backends = [DjangoFilterBackend, SearchFilter, MappedOrderingFilter]
    filterset_fields = ["project", "status", "assignee"]
    search_fields = ["title"]
    ordering_fields = ["priority", "priority_order", "created_at"]

    def get_queryset(self):
        return selectors.task_list(user=self.request.user)

    def create(self, request):
        s = TaskCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        task = services.task_create(
            actor=request.user,
            project_id=s.validated_data["project"],
            title=s.validated_data["title"],
            description=s.validated_data["description"],
            status=s.validated_data["status"],
            priority=s.validated_data["priority"],
            assignee_id=s.validated_data["assignee"],
        )
        return Response(TaskSerializer(task).data, status=201)

    def partial_update(self, request, pk=None):
        s = TaskUpdateSerializer(data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        task = services.task_update(
            actor=request.user,
            task_id=pk,
            data=s.validated_data,
        )
        return Response(TaskSerializer(task).data)

    def destroy(self, request, pk=None):
        services.task_delete(actor=request.user, task_id=pk)
        return Response(status=204)

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        queryset = selectors.task_comment_list(user=request.user, task_id=pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(CommentSerializer(queryset, many=True).data)


# ---------------- COMMENT ----------------

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return selectors.comment_list(user=self.request.user)

    def create(self, request):
        s = CommentCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        comment = services.comment_create(
            author=request.user,
            task_id=s.validated_data["task"],
            text=s.validated_data["text"],
        )
        return Response(CommentSerializer(comment).data, status=201)
