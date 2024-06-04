from rest_framework import serializers
from .models import CustomUser, Contributor, Project, Issue, Comment
from django.contrib.auth.password_validation import validate_password
from typing import Any, Dict


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    can_be_contacted = serializers.BooleanField(required=True)
    can_data_be_shared = serializers.BooleanField(required=True)
    age = serializers.IntegerField(required=True)

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
        Validate password and age fields.
        """
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            raise serializers.ValidationError(
                {"password": "Password fields did not match."}
            )

        if attrs.get("age", 0) < 18:
            raise serializers.ValidationError(
                {"age": "You must be at least 18 years old to register."}
            )

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        """
        Create a new CustomUser instance.
        """
        validated_data.pop("password2")

        can_be_contacted = validated_data.pop("can_be_contacted")
        can_data_be_shared = validated_data.pop("can_data_be_shared")
        age = validated_data.pop("age")

        user = CustomUser.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            age=age,
            can_be_contacted=can_be_contacted,
            can_data_be_shared=can_data_be_shared,
        )

        user.set_password(validated_data["password"])
        user.save()

        return user

    def update(
        self, instance: CustomUser, validated_data: Dict[str, Any]
    ) -> CustomUser:
        """
        Update an existing CustomUser instance.
        """
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.can_be_contacted = validated_data.get(
            "can_be_contacted", instance.can_be_contacted
        )
        instance.can_data_be_shared = validated_data.get(
            "can_data_be_shared", instance.can_data_be_shared
        )
        instance.age = validated_data.get("age", instance.age)

        if instance.age < 18:
            raise serializers.ValidationError(
                {"age": "You must be at least 18 years old to update this field."}
            )

        password = validated_data.get("password", None)
        password2 = validated_data.get("password2", None)
        if password and password2:
            if password == password2:
                instance.set_password(password)
            else:
                raise serializers.ValidationError(
                    {"password": "Password fields did not match."}
                )

        instance.save()
        return instance


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
        fields = ["user", "username", "project", "role"]
        read_only_fields = ["project", "role"]


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
