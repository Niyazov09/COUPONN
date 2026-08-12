from django.contrib.auth.models import User
from django.test import TestCase

from tracker.exceptions import NotFoundError
from tracker.models import Comment, Project, Task
from tracker.selectors import (
    comment_list,
    project_get,
    project_list,
    task_comment_list,
    task_get,
    task_list,
)


class ProjectListTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.member = User.objects.create_user("member")
        self.stranger = User.objects.create_user("stranger")

        self.project = Project.objects.create(name="P", owner=self.owner)
        self.project.members.add(self.member)

        self.foreign_project = Project.objects.create(
            name="Foreign", owner=self.stranger
        )

    def test_owner_sees_own_project(self):
        result = project_list(user=self.owner)
        self.assertIn(self.project, result)

    def test_member_sees_project(self):
        result = project_list(user=self.member)
        self.assertIn(self.project, result)

    def test_project_list_does_not_contain_foreign_project(self):
        result = project_list(user=self.owner)
        self.assertNotIn(self.foreign_project, result)


class ProjectGetTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.stranger = User.objects.create_user("stranger")
        self.project = Project.objects.create(name="P", owner=self.owner)

    def test_stranger_cannot_get_invisible_project(self):
        with self.assertRaises(NotFoundError):
            project_get(user=self.stranger, project_id=self.project.pk)

    def test_missing_project_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            project_get(user=self.owner, project_id=999999)


class TaskListTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.member = User.objects.create_user("member")
        self.stranger = User.objects.create_user("stranger")

        self.project = Project.objects.create(name="P", owner=self.owner)
        self.project.members.add(self.member)

        self.task = Task.objects.create(project=self.project, title="T1")

    def test_task_list_empty_for_stranger(self):
        result = task_list(user=self.stranger)
        self.assertEqual(result.count(), 0)

    def test_task_list_contains_task_for_owner(self):
        result = task_list(user=self.owner)
        self.assertIn(self.task, result)

    def test_task_list_contains_task_for_member(self):
        result = task_list(user=self.member)
        self.assertIn(self.task, result)


class TaskGetTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.stranger = User.objects.create_user("stranger")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.task = Task.objects.create(project=self.project, title="T1")

    def test_stranger_cannot_get_invisible_task(self):
        with self.assertRaises(NotFoundError):
            task_get(user=self.stranger, task_id=self.task.pk)


class TaskCommentListTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.stranger = User.objects.create_user("stranger")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.task = Task.objects.create(project=self.project, title="T1")
        self.comment = Comment.objects.create(
            task=self.task, author=self.owner, text="hi"
        )

    def test_owner_sees_comments(self):
        result = task_comment_list(user=self.owner, task_id=self.task.pk)
        self.assertIn(self.comment, result)

    def test_stranger_gets_not_found_for_invisible_task(self):
        with self.assertRaises(NotFoundError):
            task_comment_list(user=self.stranger, task_id=self.task.pk)


class CommentListTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.stranger = User.objects.create_user("stranger")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.task = Task.objects.create(project=self.project, title="T1")
        self.comment = Comment.objects.create(
            task=self.task, author=self.owner, text="hi"
        )

    def test_comment_list_empty_for_stranger(self):
        result = comment_list(user=self.stranger)
        self.assertEqual(result.count(), 0)

    def test_comment_list_contains_comment_for_owner(self):
        result = comment_list(user=self.owner)
        self.assertIn(self.comment, result)
