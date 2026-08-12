from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ProjectViewSet, TaskViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="projects")
router.register("tasks", TaskViewSet, basename="tasks")
router.register("comments", CommentViewSet, basename="comments")

urlpatterns = [
    path("", include(router.urls)),
]
