from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, TaskViewSet, CommentViewSet


router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="projects")
router.register("tasks", TaskViewSet, basename="tasks")
router.register("comments", CommentViewSet, basename="comments")

urlpatterns = [
    path("", include(router.urls)),
]