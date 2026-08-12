from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from tracker.models import Comment, Project, Task


class AuthTests(APITestCase):
    def test_request_without_token_returns_401(self):
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjectApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="12345678")
        self.member = User.objects.create_user("member", password="12345678")
        self.stranger = User.objects.create_user("stranger", password="12345678")

        self.project = Project.objects.create(name="P", owner=self.owner)
        self.project.members.add(self.member)

        self.foreign_project = Project.objects.create(
            name="Foreign", owner=self.stranger
        )

    def test_create_project_sets_owner_to_current_user(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post("/api/projects/", {"name": "New"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], self.owner.username)

    def test_get_foreign_project_returns_404(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(f"/api/projects/{self.foreign_project.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_member_can_patch_project(self):
        # Ф-2: PATCH /api/projects/{id}/ участником -> 200
        self.client.force_authenticate(self.member)
        response = self.client.patch(
            f"/api/projects/{self.project.pk}/", {"name": "Renamed"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_member_by_non_owner_returns_403(self):
        self.client.force_authenticate(self.member)
        response = self.client.post(
            f"/api/projects/{self.project.pk}/add_member/",
            {"user_id": self.stranger.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_member_returns_serialized_project(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            f"/api/projects/{self.project.pk}/add_member/",
            {"user_id": self.stranger.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.stranger.username, response.data["members"])


class TaskApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="12345678")
        self.member = User.objects.create_user("member", password="12345678")
        self.stranger = User.objects.create_user("stranger", password="12345678")

        self.project = Project.objects.create(name="P", owner=self.owner)
        self.project.members.add(self.member)

        self.foreign_project = Project.objects.create(
            name="Foreign", owner=self.stranger
        )

    def test_create_task_in_foreign_project_returns_403(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/api/tasks/",
            {"project": self.foreign_project.pk, "title": "X"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_with_non_member_assignee_returns_400(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/api/tasks/",
            {
                "project": self.project.pk,
                "title": "X",
                "assignee": self.stranger.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {"assignee": ["Исполнитель должен быть участником проекта."]},
        )

    def test_member_can_delete_task(self):
        # Ф-3: DELETE /api/tasks/{id}/ участником -> 204
        task = Task.objects.create(project=self.project, title="T1")
        self.client.force_authenticate(self.member)
        response = self.client.delete(f"/api/tasks/{task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_task_comments_endpoint_for_member_returns_200(self):
        # Ф-1: GET /api/tasks/{id}/comments/ работает
        task = Task.objects.create(project=self.project, title="T1")
        Comment.objects.create(task=task, author=self.owner, text="hi")
        self.client.force_authenticate(self.member)
        response = self.client.get(f"/api/tasks/{task.pk}/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_comments_endpoint_for_stranger_returns_404(self):
        # Ф-1: невидимая задача -> 404
        task = Task.objects.create(project=self.project, title="T1")
        self.client.force_authenticate(self.stranger)
        response = self.client.get(f"/api/tasks/{task.pk}/comments/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ordering_by_priority_puts_high_first(self):
        # Ф-4: ?ordering=priority сортирует семантически
        Task.objects.create(project=self.project, title="Low", priority="low")
        Task.objects.create(project=self.project, title="High", priority="high")
        Task.objects.create(project=self.project, title="Medium", priority="medium")

        self.client.force_authenticate(self.owner)
        response = self.client.get("/api/tasks/", {"ordering": "priority"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(results[0]["title"], "High")

    def test_status_filter_returns_correct_subset(self):
        Task.objects.create(project=self.project, title="Todo", status="todo")
        Task.objects.create(project=self.project, title="Done", status="done")

        self.client.force_authenticate(self.owner)
        response = self.client.get("/api/tasks/", {"status": "done"})
        results = response.data.get("results", response.data)
        titles = {t["title"] for t in results}
        self.assertEqual(titles, {"Done"})

    def test_assignee_filter_returns_correct_subset(self):
        Task.objects.create(
            project=self.project, title="Mine", assignee=self.member
        )
        Task.objects.create(project=self.project, title="Nobody's")

        self.client.force_authenticate(self.owner)
        response = self.client.get("/api/tasks/", {"assignee": self.member.pk})
        results = response.data.get("results", response.data)
        titles = {t["title"] for t in results}
        self.assertEqual(titles, {"Mine"})

    def test_patch_task_with_project_returns_400(self):
        # Ф-5: смена project через PATCH запрещена
        other_project = Project.objects.create(
            name="Other", owner=self.owner
        )
        task = Task.objects.create(project=self.project, title="T1")
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            f"/api/tasks/{task.pk}/", {"project": other_project.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="12345678")
        self.project = Project.objects.create(name="P", owner=self.owner)
        self.task = Task.objects.create(project=self.project, title="T1")

    def test_create_comment_sets_author(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/api/comments/", {"task": self.task.pk, "text": "hi"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.owner.username)
