from django.contrib import admin

from .models import Project, Task, Comment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created_at")
    search_fields = ("name", "owner__username")
    list_filter = ("created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "project",
        "status",
        "priority",
        "assignee",
        "created_at",
    )
    search_fields = (
        "title",
        "project__name",
        "assignee__username",
    )
    list_filter = (
        "status",
        "priority",
        "created_at",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "author",
        "created_at",
    )
    search_fields = (
        "task__title",
        "author__username",
        "text",
    )
    list_filter = ("created_at",)