from rest_framework.permissions import BasePermission
from .models import Project, Contributor, Issue, Comment
from django.http import HttpRequest
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request


class UserPermission(BasePermission):
    def has_permission(self, request: Request, view: ViewSet) -> bool:
        """
        Returns permissions based on the action.
        """
        if view.action == "create":
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request: Request, view: ViewSet, obj) -> bool:
        """
        Object-level permission check.
        """
        if view.action in ["retrieve", "update", "partial_update", "destroy"]:
            return obj == request.user


class ContributorPermission(BasePermission):
    """
    Contributors can [List, Retrieve],
    Projects Authors can [List, Retrieve, Put, Patch, Delete]
    """

    def has_permission(self, request: HttpRequest, view: ViewSet) -> bool:

        if view.action in ["create", "update", "partial_update", "destroy"]:
            return Project.objects.filter(
                author=request.user, id=view.kwargs["project_pk"]
            ).exists()

        return Contributor.objects.filter(
            user=request.user, project_id=view.kwargs["project_pk"]
        ).exists()


class ProjectPermission(BasePermission):
    """
    AllowAny [Create],
    Projects Authors can [List, Retrieve, Put, Patch, Delete]
    Contributors can [List, Retrieve],
    """

    def has_object_permission(
        self, request: HttpRequest, view: ViewSet, obj: Project
    ) -> bool:
        try:
            project = Project.objects.get(id=view.kwargs["pk"])
        except Project.DoesNotExist:
            return False

        if view.action in ["update", "partial_update", "destroy"]:
            return request.user == obj.author
        return project in Project.objects.filter(contributors__user=request.user)


class IssuePermission(BasePermission):
    """
    Issues Authors can [List, Retrieve, Put, Patch, Delete]
    Contributors can [Create, List, Retrieve],
    """

    def has_permission(self, request: HttpRequest, view: ViewSet) -> bool:
        project = Project.objects.get(id=view.kwargs["project_pk"])
        if view.action in ["update", "partial_update", "destroy"]:
            issue = Issue.objects.get(id=view.kwargs["pk"], project=project)
            return request.user == issue.author
        return Contributor.objects.filter(
            user=request.user, project=project
        ).exists()


class CommentPermission(BasePermission):
    """
    Comments Authors can [List, Retrieve, Put, Patch, Delete]
    Contributors can [Create, List, Retrieve],
    """

    def has_permission(self, request: HttpRequest, view: ViewSet) -> bool:
        project = Project.objects.get(id=view.kwargs["project_pk"])
        issue = Issue.objects.get(id=view.kwargs["issue_pk"])
        if view.action in ["update", "partial_update", "destroy"]:
            comment = Comment.objects.get(uuid=view.kwargs["pk"], issue=issue)
            return request.user == comment.author
        return Contributor.objects.filter(
            user=request.user, project=project
        ).exists()
