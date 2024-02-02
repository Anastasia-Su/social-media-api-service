from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Post, Profile


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    user = serializers.CharField(
        read_only=True, source="user.email"
    )
    hashtags = TagListSerializerField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "user",
            "image",
            "hashtags",
            "follow"
        ]


class PostListSerializer(PostSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "user",
            "image",
            "hashtags"
        ]


class PostDetailSerializer(PostListSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "user",
            "image",
            "hashtags"
        ]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "bio",
            "image",
            "follow"
        ]


class ProfileListSerializer(ProfileSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    followers = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)

    def get_followers(self, obj):
        return f"{len(obj.followers.all())} user(s)"

    def get_is_following(self, obj):
        return f"{len(obj.is_following.all())} user(s)"

    def get_user(self, obj):
        return f"{obj.first_name} {obj.last_name} ({obj.user.email})"

    class Meta:
        model = Profile
        fields = ["id", "user", "image", "followers", "is_following"]


class ProfileDetailSerializer(ProfileSerializer):
    followers = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)

    def get_followers(self, obj):
        return [
            f"{member.first_name} {member.last_name} ({member.email})"
            for member in obj.followers.all()
        ]

    def get_is_following(self, obj):
        return [
            (
             f"{member.profile.first_name} "
             f"{member.profile.last_name} "
             f"({member.profile.user.email})"
             )
            for member in obj.is_following.all()
        ]

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "bio",
            "image",
            "is_following",
            "followers"
        ]


class FollowActionSerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ["follow"]


class FollowPostActionSerializer(PostSerializer):
    class Meta:
        model = Post
        fields = ["follow"]


