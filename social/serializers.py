from django.db import IntegrityError
from rest_framework import serializers
from .models import Post, Profile


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "description"]


class PostListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(
        read_only=True, source="user.email"
    )

    class Meta:
        model = Post
        fields = ["id", "title", "description", "user"]


class ProfileSerializer(serializers.ModelSerializer):
    # first_name = serializers.CharField(source='user.first_name', read_only=True)
    # last_name = serializers.CharField(source='user.last_name', read_only=True)
    # bio = serializers.CharField(source='user.bio', read_only=True)
    class Meta:
        model = Profile
        fields = ["id", "first_name", "last_name", "bio", "image"]


class ProfileListSerializer(ProfileSerializer):
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        return f"{obj.first_name} {obj.last_name} ({obj.user.email})"

    class Meta:
        model = Profile
        fields = ["id", "user", "image"]


class ProfileDetailSerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ["id", "user", "first_name", "last_name", "bio", "image"]


class ProfileImageSerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ["id", "image"]


