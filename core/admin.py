from django.contrib import admin
from .models import CustomUser, Project, Contributor, Issue, Comment


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "can_be_contacted",
        "can_data_be_shared",
        "age",
    )
    search_fields = ("username", "email")
    list_filter = (
        "is_staff",
        "is_superuser",
        "can_be_contacted",
        "can_data_be_shared",
        "age",
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "type", "author")
    search_fields = ("title", "description")
    list_filter = ("type", "author")


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "role")
    search_fields = ("user__username", "project__title")
    list_filter = ("role",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "description",
        "priority",
        "tag",
        "status",
        "project",
        "author",
    )
    search_fields = ("title", "description")
    list_filter = ("priority", "tag", "status", "project", "author")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "author", "issue", "created_time")
    search_fields = ("text", "author__username", "issue__title")
    list_filter = ("created_time", "author", "issue")
