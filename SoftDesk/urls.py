from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core import views

router = DefaultRouter()
router.register(r"projects", views.ProjectViewSet, basename="project")
router.register(
    r"projects/(?P<project_pk>[^/.]+)/contributors",
    views.ContributorViewSet,
    basename="contributor",
)
router.register(
    r"projects/(?P<project_pk>[^/.]+)/issues", views.IssueViewSet, basename="issue"
)
router.register(
    r"projects/(?P<project_pk>[^/.]+)/issues/(?P<issue_pk>[^/.]+)/comments",
    views.CommentViewSet,
    basename="comment",
)
router.register(r"users", views.CustomUserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/signup/",
        views.CustomUserViewSet.as_view({"post": "create"}),
        name="signup",
    ),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]
