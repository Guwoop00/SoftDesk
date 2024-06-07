from rest_framework import serializers
from .models import CustomUser, Contributor, Project, Issue, Comment
from django.contrib.auth.password_validation import validate_password
from typing import Any, Dict, Optional


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    """
    email: serializers.EmailField = serializers.EmailField(required=True)
    password: serializers.CharField = serializers.CharField(write_only=True, required=True,
                                                            validators=[validate_password])
    password2: serializers.CharField = serializers.CharField(write_only=True, required=True)

    class Meta:
        model: Any = CustomUser
        fields: tuple = ('username', 'email', 'password', 'password2', 'can_be_contacted', 'can_data_be_shared', 'age')

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the passwords and age fields.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields did not match."})

        if attrs.get("age", 0) < 18:
            raise serializers.ValidationError({"age": "You must be at least 18 years old to register."})

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Create a new CustomUser instance.
        """
        validated_data.pop('password2')
        user: CustomUser = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance: CustomUser, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Update an existing CustomUser instance.
        """
        validated_data.pop('password2', None)
        password: Optional[str] = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """

    class Meta:
        model: Any = Project
        fields: list = ["id", "title", "description", "type", "author", "created_time"]
        read_only_fields: list = ["id", "author", "created_time"]


class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer for Contributor model.
    """

    username: serializers.CharField = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model: Any = Contributor
        fields: list = ["user", "username", "project"]
        read_only_fields: list = ["project"]


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model.
    """

    author_username: serializers.CharField = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model: Any = Issue
        fields: list = [
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
        read_only_fields: list = [
            "project",
            "created_time",
            "author",
        ]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """

    author_username: serializers.CharField = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model: Any = Comment
        fields: list = ["uuid", "text", "issue", "author", "author_username"]
        read_only_fields: list = ["issue", "author"]
