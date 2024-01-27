from rest_framework import serializers
from .models import Post


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
