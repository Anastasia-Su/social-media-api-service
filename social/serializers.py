from rest_framework import serializers
from taggit.models import Tag
from taggit.serializers import TaggitSerializer, TagListSerializerField

from .models import Post, Profile, Comment


def populate_comment_data(query):
    comment_data = []
    for comment in query:
        comment_data.append(
            {
                "text": comment.text,
                "user": str(comment.user),
                "is_reply": comment.is_reply,
                "parent": comment.parent.id if comment.parent else None,
            }
        )

    return comment_data


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    user = serializers.CharField(read_only=True, source="user.email")
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
        ]


class PostListSerializer(PostSerializer):
    liked_by = serializers.SerializerMethodField(read_only=True)

    def get_liked_by(self, obj):
        return f"{len(obj.liked_by.all())} user(s)"

    class Meta:
        model = Post
        fields = [
            "id", "title", "description", "user", "image", "hashtags", "liked_by"
        ]


class PostDetailSerializer(PostListSerializer):
    comments = serializers.SerializerMethodField(read_only=True)
    liked_by = serializers.SerializerMethodField(read_only=True)

    def get_liked_by(self, obj):
        return [
            f"{member.first_name} {member.last_name} ({member.email}): {obj.like}"
            for member in obj.liked_by.all()
        ]

    def get_comments(self, obj):
        comments = obj.post_comments.all()
        return populate_comment_data(comments)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "description",
            "user",
            "image",
            "hashtags",
            "comments",
            "liked_by"
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
        fields = [
            "id", "user", "image", "followers", "is_following"
        ]


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
            "followers",
        ]


class FollowActionSerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ["follow"]


class FollowPostActionSerializer(PostSerializer):
    class Meta:
        model = Post
        fields = ["id", "follow"]


class LikePostActionSerializer(PostSerializer):
    class Meta:
        model = Post
        fields = ["id", "like"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id", "post", "user", "text", "is_reply", "parent"
        ]


class CommentListSerializer(CommentSerializer):
    commented_by = serializers.SerializerMethodField(read_only=True)
    post = serializers.SerializerMethodField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)

    def get_post(self, obj):
        if obj.parent:
            return obj.parent.post.title
        return obj.post.title

    def get_author(self, obj):
        root = obj.post.user
        if obj.parent:
            root = obj.parent.post.user
        return f"{root.profile.first_name} " f"{root.profile.last_name} ({root.email})"

    def get_commented_by(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name} ({obj.user.email})"

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "commented_by",
            "text",
            "is_reply",
            "parent"
        ]


class CommentDetailSerializer(CommentListSerializer):
    replies = serializers.SerializerMethodField(read_only=True)

    def get_replies(self, obj):
        comments = obj.comments.filter(is_reply=True)
        return populate_comment_data(comments)

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "commented_by",
            "text",
            "is_reply",
            "parent",
            "replies",
        ]


class CommentCreateSerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = ["id", "text"]


class CommentReplySerializer(CommentSerializer):
    class Meta:
        model = Comment
        fields = ["id", "text"]
