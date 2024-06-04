from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import CustomUser, Project, Issue, Comment, Contributor
from .serializers import (
    CustomUserSerializer,
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)
from .permissions import (
    ProjectPermission,
    ContributorViewsetPermission,
    IssuePermission,
    CommentPermission,
)
from typing import Union


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CustomUser.
    """

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self) -> Union[AllowAny, IsAuthenticated]:
        """
        Returns permissions based on the action.
        """
        if self.action in ["create"]:
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def get_object(self) -> CustomUser:
        """
        Returns the CustomUser object based on the action.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return self.request.user
        return super().get_object()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Project.
    """

    permission_classes = [ProjectPermission]
    serializer_class = ProjectSerializer

    def get_queryset(self) -> Project:
        """
        Returns queryset filtered by user.
        """
        return Project.objects.filter(contributors__user=self.request.user)

    def perform_create(self, serializer: ProjectSerializer) -> None:
        """
        Performs creation of a new project.
        """
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(
            user=self.request.user, project=project, role="AUTHOR"
        )


class ContributorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Contributor.
    """

    permission_classes = [ContributorViewsetPermission]
    serializer_class = ContributorSerializer

    def get_queryset(self) -> Contributor:
        """
        Returns queryset filtered by project.
        """
        project_id = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, id=project_id)
        return Contributor.objects.filter(project=project)

    def perform_create(self, serializer: ContributorSerializer) -> Response:
        """
        Performs creation of a new contributor.
        """
        project_id = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, id=project_id)
        data = self.request.data.copy()
        data["project"] = project.id

        serializer = ContributorSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=data["user"])
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "This user does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Contributor.objects.filter(user=user, project=project).exists():
            return Response(
                {"error": "This user has already been added."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(project=project, user=user, role="CONTRIBUTOR")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs) -> Response:
        """
        Retrieves a contributor.
        """
        project_id = self.kwargs.get("project_pk")
        user_id = self.kwargs.get("pk")
        project = get_object_or_404(Project, id=project_id)
        contributor = get_object_or_404(Contributor, user_id=user_id, project=project)
        serializer = self.get_serializer(contributor)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        Destroys a contributor.
        """
        project_id = self.kwargs.get("project_pk")
        user_id = self.kwargs.get("pk")
        project = get_object_or_404(Project, id=project_id)
        contributor = get_object_or_404(Contributor, user_id=user_id, project=project)

        if contributor.role == "AUTHOR":
            raise ValidationError("Project author cannot be deleted.")

        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Issue.
    """

    permission_classes = [IssuePermission]
    serializer_class = IssueSerializer

    def get_queryset(self) -> Issue:
        """
        Returns queryset filtered by project.
        """
        project_id = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, id=project_id)
        return Issue.objects.filter(project=project)

    def perform_create(self, serializer: IssueSerializer) -> None:
        """
        Performs creation of a new issue.
        """
        project_id = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, id=project_id)
        serializer.save(project=project, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Comment.
    """

    permission_classes = [CommentPermission]
    serializer_class = CommentSerializer

    def get_queryset(self) -> Comment:
        """
        Returns queryset filtered by issue.
        """
        issue_id = self.kwargs.get("issue_pk")
        issue = get_object_or_404(Issue, id=issue_id)
        return Comment.objects.filter(issue=issue)

    def perform_create(self, serializer: CommentSerializer) -> None:
        """
        Performs creation of a new comment.
        """
        issue_id = self.kwargs.get("issue_pk")
        issue = get_object_or_404(Issue, id=issue_id)
        serializer.save(issue=issue, author=self.request.user)
