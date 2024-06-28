from rest_framework import serializers
from .models import CustomUser, Contributor, Project, Issue, Comment
from django.contrib.auth.password_validation import validate_password
from typing import Any, Dict
from django.contrib.auth.hashers import make_password


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    """

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True)

    can_be_contacted = serializers.BooleanField()
    can_data_be_shared = serializers.BooleanField()
    age = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "can_be_contacted",
            "can_data_be_shared",
            "age",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that password and password2 match.
        """
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError("Password fields did not match.")
        return attrs

    def validate_age(self, value: int) -> int:
        """
        Validate age field.
        """
        if value < 18:
            raise serializers.ValidationError("You must be at least 18 years old to update this field.")
        return value

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Create a new CustomUser instance.
        """
        validated_data.pop('password2', None)
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class CustomUserUpdateSerializer(CustomUserSerializer):
    """
    Serializer for updating CustomUser model.
    """

    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)
    age = serializers.IntegerField(required=False)

    def update(self, instance: CustomUser, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Update an existing CustomUser instance.
        """

        if "password" in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
            validated_data.pop('password')

        return super().update(instance, validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """

    class Meta:
        model = Project
        fields = ["id", "title", "description", "type", "author", "created_time"]
        read_only_fields = ["id", "author", "created_time"]


class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer for Contributor model.
    """

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Contributor
        fields = ["user", "username", "project_id"]
        read_only_fields = ["project"]

    def validate_delete(self, contributor):
        """
        Validate if the contributor can be deleted.
        """
        if contributor.user == contributor.project.author:
            raise serializers.ValidationError("Project author cannot be deleted.")
        return contributor


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model.
    """

    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "tag",
            "status",
            "project",
            "author_username",
            "author",
            "assignee",
            "created_time",
        ]
        read_only_fields = [
            "project",
            "created_time",
            "author",
        ]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """

    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["uuid", "text", "issue", "author", "author_username"]
        read_only_fields = ["issue", "author"]
