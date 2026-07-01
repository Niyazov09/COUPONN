from django.test import TestCase


from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Project


class ProjectTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="12345678"
        )

    def test_create_project_requires_auth(self):
        response = self.client.post(
            "/api/projects/",
            {"name": "Project"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_create_project_authenticated(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            "/api/projects/",
            {"name": "Project"}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

