from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import CustomUser, Project, Issue, Comment, Contributor
from .serializers import (
    CustomUserSerializer,
    CustomUserUpdateSerializer,
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)
from .permissions import (
    UserPermission,
    ProjectPermission,
    ContributorPermission,
    IssuePermission,
    CommentPermission,
)


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CustomUser.
    """
    permission_classes = [UserPermission]

    def get_queryset(self) -> CustomUser:
        """
        Returns queryset of users.
        """
        return CustomUser.objects.all()

    def get_serializer_class(self):
        """
        Returns the right serializer to use.
        """
        if self.action in ["update", "partial_update"]:
            return CustomUserUpdateSerializer
        return CustomUserSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Project.
    """
    permission_classes = [IsAuthenticated, ProjectPermission]
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
            user=self.request.user, project=project)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Contributor.
    """

    permission_classes = [IsAuthenticated, ContributorPermission]
    serializer_class = ContributorSerializer

    def get_queryset(self) -> Contributor:
        """
        Returns queryset filtered by project.
        """
        return Contributor.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer: ContributorSerializer) -> Response:
        """
        Performs creation of a new contributor.
        """
        project_id = self.kwargs.get("project_pk")
        project = get_object_or_404(Project, id=project_id)
        data = self.request.data.copy()
        data["project"] = project.id
        serializer = ContributorSerializer(data=data)

        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(id=serializer.validated_data['user'].id)
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

            serializer.save(project=project, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

        serializer = ContributorSerializer(contributor)
        serializer.validate_delete(contributor)

        contributor.delete()
        return Response('Contributor successfully deleted.', status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Issue.
    """

    permission_classes = [IsAuthenticated, IssuePermission]
    serializer_class = IssueSerializer

    def get_queryset(self) -> Issue:
        """
        Returns queryset filtered by project.
        """
        return Issue.objects.filter(project_id=self.kwargs["project_pk"])

    def perform_create(self, serializer: IssueSerializer) -> None:
        """
        Performs creation of a new issue.
        """
        serializer.save(project_id=self.kwargs["project_pk"], author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Comment.
    """

    permission_classes = [IsAuthenticated, CommentPermission]
    serializer_class = CommentSerializer

    def get_queryset(self) -> Comment:
        """
        Returns queryset filtered by issue.
        """
        return Comment.objects.filter(issue_id=self.kwargs["issue_pk"])

    def perform_create(self, serializer: CommentSerializer) -> None:
        """
        Performs creation of a new comment.
        """
        project_id = self.kwargs.get("project_pk")
        issue_id = self.kwargs.get("issue_pk")
        get_object_or_404(Project, id=project_id)
        issue = get_object_or_404(Issue, id=issue_id)
        serializer.save(issue=issue, author=self.request.user)
