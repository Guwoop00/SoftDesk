from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import uuid
from typing import Optional


class CustomUser(AbstractUser):  # cf CustomUserSerializer
    """
    Custom model for User

    Attributes:
        can_be_contacted (bool)
        can_data_be_shared (bool)
        age (int)
    """

    can_be_contacted: bool = models.BooleanField(default=False)
    can_data_be_shared: bool = models.BooleanField(default=False)
    age: int = models.IntegerField(default=18)

    def __str__(self) -> str:
        return self.username


class Project(models.Model):
    """
    Model for project.

    Attributes:
        title (str)
        description (str)
        type (str)
        author (CustomUser)
        created_time (datetime)
    """

    title: str = models.CharField(max_length=100)
    description: str = models.TextField()
    type: str = models.CharField(
        max_length=10,
        choices=[
            ("BACKEND", "Back-end"),
            ("FRONTEND", "Front-end"),
            ("IOS", "iOS"),
            ("ANDROID", "Android"),
        ],
    )
    author: CustomUser = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name="projects", on_delete=models.CASCADE
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Contributor(models.Model):
    """
    Model for Contributor.

    Attributes:
        user (CustomUser)
        project (Project)
        role (str)
    """

    user: CustomUser = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="contributions",
        on_delete=models.CASCADE,
    )
    project: Project = models.ForeignKey(
        Project, related_name="contributors", on_delete=models.CASCADE
    )
    role: str = models.CharField(
        max_length=15,
        choices=[("AUTHOR", "Author"), ("CONTRIBUTOR", "Contributor")],
        default="CONTRIBUTOR",
    )

    class Meta:
        unique_together = ("user", "project")

    def __str__(self) -> str:
        return f"{self.user} - {self.project}"


class Issue(models.Model):
    """
    Model for Issue.

    Attributes:
        title (str)
        description (str)
        priority (str)
        tag (CustomUser)
        status (str)
        project (Project)
        author (CustomUser)
        assignee (CustomUser)
        created_time (datetime)
    """

    title: str = models.CharField(max_length=100)
    description: str = models.TextField()
    priority: str = models.CharField(
        max_length=10, choices=[("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")]
    )
    tag: str = models.CharField(
        max_length=10,
        choices=[("BUG", "Bug"), ("FEATURE", "Feature"), ("TASK", "Task")],
    )
    status: str = models.CharField(
        max_length=15,
        choices=[
            ("TODO", "To Do"),
            ("IN_PROGRESS", "In Progress"),
            ("FINISHED", "Finished"),
        ],
        default="TODO",
    )
    project: Project = models.ForeignKey(
        Project, related_name="issues", on_delete=models.CASCADE
    )
    author: CustomUser = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="created_issues",
        on_delete=models.CASCADE,
    )
    assignee: Optional[CustomUser] = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="assigned_issues",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """
    Model for Comment.

    Attributes:
        text (str)
        issue (Issue)
        author (CustomUser)
        created_time (datetime)
        uuid (models.UUIDField)
    """

    text: str = models.TextField()
    issue: Issue = models.ForeignKey(
        Issue, related_name="comments", on_delete=models.CASCADE
    )
    author: CustomUser = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name="comments", on_delete=models.CASCADE
    )
    created_time = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )

    def __str__(self) -> str:
        return self.text[:50]
