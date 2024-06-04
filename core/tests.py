from django.test import TestCase
from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APIClient
from .models import CustomUser, Project, Contributor, Issue, Comment


class APITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password123"
        )
        self.user2 = CustomUser.objects.create_user(
            username="contributor", password="password123"
        )
        self.client.force_authenticate(user=self.user)

    def test_signup(self):
        url = reverse("signup")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "password2": "newpassword123",
            "age": 25,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_project(self):
        url = reverse("project-list")
        data = {
            "title": "New Project",
            "description": "This is a new project",
            "type": "BACKEND",
            "author": self.user.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().title, "New Project")

    def test_add_contributor(self):
        project = Project.objects.create(
            title="Project",
            description="Test Project",
            type="BACKEND",
            author=self.user,
        )
        url = reverse("contributor-list", args=[project.id])
        data = {"user": self.user2.id, "project": project.id, "role": "CONTRIBUTOR"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contributor.objects.count(), 1)

    def test_create_issue(self):
        project = Project.objects.create(
            title="Project",
            description="Test Project",
            type="BACKEND",
            author=self.user,
        )
        contributor = Contributor.objects.create(
            user=self.user, project=project, role="AUTHOR"
        )
        url = reverse("issue-list", args=[project.id])
        data = {
            "title": "New Issue",
            "description": "Issue description",
            "priority": "HIGH",
            "tag": "BUG",
            "status": "TODO",
            "contributor": contributor.id,
            "author": self.user.id,
            "project": project.id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Issue.objects.count(), 1)
        self.assertEqual(Issue.objects.get().title, "New Issue")

    def test_create_comment(self):
        project = Project.objects.create(
            title="Project",
            description="Test Project",
            type="BACKEND",
            author=self.user,
        )
        issue = Issue.objects.create(
            title="Issue",
            description="Issue description",
            project=project,
            author=self.user,
            priority="HIGH",
            tag="BUG",
            status="TODO",
        )
        url = reverse("comment-list", args=[project.id, issue.id])
        data = {"text": "This is a comment", "author": self.user.id, "issue": issue.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().text, "This is a comment")

    def test_delete_project(self):
        project = Project.objects.create(
            title="Project",
            description="Test Project",
            type="BACKEND",
            author=self.user,
        )
        url = reverse("project-detail", args=[project.id])
        print(f"URL for deleting project: {url}")
        response = self.client.delete(url)
        print(f"Resolved view: {resolve(url).view_name}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)


if __name__ == "__main__":
    import unittest

    unittest.main()
