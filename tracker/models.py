from django.contrib.auth.models import User
from django.db import models
from django.db.models import Case, IntegerField, Q, When


class ProjectQuerySet(models.QuerySet):
    def visible_to(self, user):
        return self.filter(Q(owner=user) | Q(members=user)).distinct()


class Project(models.Model):
    name = models.CharField(max_length=200)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_projects"
    )

    members = models.ManyToManyField(
        User,
        related_name="projects",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def is_member(self, user):
        return (
            user == self.owner or
            self.members.filter(id=user.id).exists()
        )


class TaskQuerySet(models.QuerySet):
    def visible_to(self, user):
        return self.filter(
            Q(project__owner=user) | Q(project__members=user)
        ).distinct()

    def with_priority_order(self):
        return self.annotate(
            priority_order=Case(
                When(priority="high", then=1),
                When(priority="medium", then=2),
                When(priority="low", then=3),
                output_field=IntegerField(),
            )
        )


class Task(models.Model):
    STATUS_CHOICES = [
        ("todo", "Todo"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="todo"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium"
    )

    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class CommentQuerySet(models.QuerySet):
    def visible_to(self, user):
        return self.filter(
            Q(task__project__owner=user) | Q(task__project__members=user)
        ).distinct()


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CommentQuerySet.as_manager()

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.username}"
