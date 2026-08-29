import time

from django.contrib.auth.models import User
from django.test import TestCase

from tracker.exceptions import BusinessValidationError, PermissionDeniedError
from tracker.models import Project, Task
from tracker.services import (
    comment_create,
    project_add_member,
    project_create,
    project_delete,
    project_update,
    task_create,
    task_delete,
    task_update,
)


class ProjectCreateTests(TestCase):
    def test_project_create_sets_owner(self):
        owner = User.objects.create_user("owner")
        project = project_create(owner=owner, name="P")
        self.assertEqual(project.owner, owner)
        self.assertEqual(project.name, "P")


class ProjectUpdateTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.member = User.objects.create_user("member")
        self.stranger = User.objects.create_user("stranger")
        self.project = Project.objects.create(name="Old", owner=self.owner)
        self.project.members.add(self.member)

    def test_member_can_rename_project(self):
        project = project_update(actor=self.member, project_id=self.project.pk, name="New")
        self.assertEqual(project.name, "New")


class ProjectDeleteTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.member = User.objects.create_user("member")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.project.members.add(self.member)

    def test_non_owner_member_cannot_delete_project(self):
        with self.assertRaises(PermissionDeniedError):
            project_delete(actor=self.member, project_id=self.project.pk)

    def test_owner_can_delete_project(self):
        project_delete(actor=self.owner, project_id=self.project.pk)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())


class ProjectAddMemberTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.member = User.objects.create_user("member")
        self.new_user = User.objects.create_user("newbie")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.project.members.add(self.member)

    def test_non_owner_cannot_add_member(self):
        with self.assertRaises(PermissionDeniedError):
            project_add_member(
                actor=self.member, project_id=self.project.pk, user_id=self.new_user.pk
            )

    def test_owner_can_add_member(self):
        project = project_add_member(
            actor=self.owner, project_id=self.project.pk, user_id=self.new_user.pk
        )
        self.assertIn(self.new_user, project.members.all())

    def test_add_member_with_missing_user_id_raises_business_error(self):
        with self.assertRaises(BusinessValidationError):
            project_add_member(actor=self.owner, project_id=self.project.pk, user_id=999999)

    def test_adding_owner_as_member_does_not_duplicate_role(self):
        # Регрессия: идемпотентность проверялась через members.filter(...),
        # а не is_member() — добавление владельца дублировало его в members.
        project = project_add_member(
            actor=self.owner, project_id=self.project.pk, user_id=self.owner.pk
        )
        self.assertFalse(project.members.filter(pk=self.owner.pk).exists())

    def test_add_member_is_idempotent(self):
        project_add_member(actor=self.owner, project_id=self.project.pk, user_id=self.new_user.pk)
        project = project_add_member(
            actor=self.owner, project_id=self.project.pk, user_id=self.new_user.pk
        )
        self.assertEqual(list(project.members.filter(pk=self.new_user.pk)).__len__(), 1)


class TaskCreateTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.member = User.objects.create_user("member")
        self.stranger = User.objects.create_user("stranger")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.project.members.add(self.member)

    def test_stranger_cannot_create_task(self):
        with self.assertRaises(PermissionDeniedError):
            task_create(actor=self.stranger, project_id=self.project.pk, title="X")

    def test_create_task_with_missing_project_raises_business_error(self):
        with self.assertRaises(BusinessValidationError):
            task_create(actor=self.owner, project_id=999999, title="X")

    def test_assignee_must_be_member(self):
        with self.assertRaises(BusinessValidationError):
            task_create(
                actor=self.owner,
                project_id=self.project.pk,
                title="X",
                assignee_id=self.stranger.pk,
            )

    def test_task_created_with_member_assignee(self):
        task = task_create(
            actor=self.owner,
            project_id=self.project.pk,
            title="X",
            assignee_id=self.member.pk,
        )
        self.assertEqual(task.assignee, self.member)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())


class TaskUpdateTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.other_project = Project.objects.create(
            name="Other", owner=User.objects.create_user("other_owner")
        )
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.task = Task.objects.create(project=self.project, title="T1")

    def test_changing_project_in_data_raises_business_error(self):
        with self.assertRaises(BusinessValidationError):
            task_update(
                actor=self.owner,
                task_id=self.task.pk,
                data={"project": self.other_project.pk},
            )

    def test_updated_at_refreshes_on_patch(self):
        # Регрессия: save(update_fields=[...]) без 'updated_at' в списке
        # не триггерит auto_now, поле оставалось временем создания.
        original_updated_at = self.task.updated_at
        time.sleep(0.01)

        task = task_update(
            actor=self.owner, task_id=self.task.pk, data={"title": "New title"}
        )

        self.assertGreater(task.updated_at, original_updated_at)

    def test_task_update_does_not_mutate_caller_dict(self):
        # Регрессия: сервис переписывал переданный словарь на месте
        # (побочный эффект на s.validated_data вызывающей стороны).
        member = User.objects.create_user("member")
        self.project.members.add(member)
        data = {"assignee": member.pk}

        task_update(actor=self.owner, task_id=self.task.pk, data=data)

        self.assertEqual(data["assignee"], member.pk)


class TaskDeleteTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.member = User.objects.create_user("member")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.project.members.add(self.member)
        self.task = Task.objects.create(project=self.project, title="T1")

    def test_member_can_delete_task(self):
        task_delete(actor=self.member, task_id=self.task.pk)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())


class CommentCreateTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner")
        self.stranger = User.objects.create_user("stranger")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.task = Task.objects.create(project=self.project, title="T1")

    def test_comment_author_is_actor(self):
        comment = comment_create(author=self.owner, task_id=self.task.pk, text="hi")
        self.assertEqual(comment.author, self.owner)

    def test_stranger_cannot_comment(self):
        with self.assertRaises(PermissionDeniedError):
            comment_create(author=self.stranger, task_id=self.task.pk, text="hi")
