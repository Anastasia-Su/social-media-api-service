from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .mixins import ToggleFollowMixin, ToggleLikeMixin
from .models import Post, Profile, Comment
from .permissions import (
    IsLoggedIn,
    IsAdminOrIfAuthenticatedReadOnly,
    IsAuthenticatedReadOnly,
)

from .serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    FollowPostActionSerializer,
    LikePostActionSerializer,
    ProfileSerializer,
    ProfileListSerializer,
    ProfileDetailSerializer,
    FollowActionSerializer,
    CommentSerializer,
    CommentCreateSerializer,
    CommentListSerializer,
    CommentDetailSerializer,
    CommentReplySerializer,
)


class PostViewSet(viewsets.ModelViewSet, ToggleLikeMixin):
    queryset = (
        Post.objects
        .select_related("user")
        .prefetch_related(
            "liked_by",
            "hashtags",
            "comments__profile",
            "comments__post_title",
            "comments__parent__profile",
            "comments__user",
            "comments__replies__user__profile",
            "comments__replies__post",
        )
    )
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    @action(
        methods=["POST"],
        detail=True,
        url_path="toggle-like",
        permission_classes=[IsAuthenticated],
    )
    def toggle_like(self, request, pk):
        post = self.get_object()
        return self.toggle_like_common(request, post)

    @action(
        methods=["POST"],
        detail=True,
        url_path="add-comment",
        permission_classes=[IsAuthenticated],
    )
    def add_comment(self, request, pk):
        post = self.get_object()
        user = request.user
        text = request.data.get("text", "")

        if request.method == "POST":
            comment = Comment.objects.create(post=post, user=user, text=text)

            serializer = self.get_serializer(comment, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action == "toggle_follow":
            return FollowPostActionSerializer

        if self.action == "toggle_like":
            return LikePostActionSerializer

        if self.action == "add_comment":
            return CommentCreateSerializer

        return PostSerializer

    def get_permissions(self):
        if self.action == "update" or self.action == "destroy":
            return [IsLoggedIn()]

        if self.action in [
            "list",
            "create",
            "toggle_follow",
            "add_comment",
            "toggle_like",
        ]:
            return [IsAuthenticated()]

        return [IsAuthenticatedReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @staticmethod
    def _split_params(qs):
        """Converts a list of string IDs to a list of strings"""
        return [tag.strip() for tag in qs.split(",")]

    def get_queryset(self):
        user = self.request.query_params.get("user")
        text = self.request.query_params.get("text")
        tags = self.request.query_params.get("tags")
        queryset = self.queryset.all()

        if user:
            queryset = queryset.filter(
                Q(user__email__icontains=user)
                | Q(user__first_name__icontains=user)
                | Q(user__last_name__icontains=user)
            )
        if text:
            queryset = queryset.filter(
                Q(title__icontains=text)
                | Q(description__icontains=text)
            )

        if tags:
            splitted_tags = self._split_params(tags)
            queryset = queryset.filter(hashtags__name__in=splitted_tags)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "text",
                type=OpenApiTypes.STR,
                description="Filter by post text (ex. ?text=post)",
            ),
            OpenApiParameter(
                "user",
                type=OpenApiTypes.STR,
                description="Filter by user (ex. ?user=j)",
            ),
            OpenApiParameter(
                "tags",
                type=OpenApiTypes.STR,
                description="Filter by tags (ex. ?tags=cats,dogs)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProfileViewSet(viewsets.ModelViewSet, ToggleFollowMixin):
    queryset = (
        Profile.objects.select_related("user")
        .prefetch_related("followers__profile", "is_following__profile")
    )
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedReadOnly,)

    @action(
        methods=["POST"],
        detail=True,
        url_path="toggle-follow",
        permission_classes=[IsAuthenticated],
    )
    def toggle_follow(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)
        return self.toggle_follow_common(request, profile)

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer

        if self.action == "retrieve":
            return ProfileDetailSerializer

        if self.action == "toggle_follow":
            return FollowActionSerializer

        return ProfileSerializer

    def get_permissions(self):
        if self.action == "update" or self.action == "destroy":
            return [IsLoggedIn()]
        if self.action in ["toggle_follow", "toggle_like"]:
            return [IsAuthenticated()]
        return [IsAuthenticatedReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        users = self.request.query_params.get("users")
        queryset = self.queryset.all()

        if users:
            users_ids = self._params_to_ints(users)
            queryset = queryset.filter(user__id__in=users_ids)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "users",
                type=OpenApiTypes.INT,
                description="Filter by user id (ex. ?users=2,3)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ILikeViewSet(PostViewSet, ProfileViewSet, ToggleLikeMixin):
    @action(
        methods=["POST"],
        detail=True,
        url_path="toggle-like",
        permission_classes=[IsAuthenticated],
    )
    def toggle_like(self, request, pk):
        post = self.get_object()
        return self.toggle_like_common(request, post)

    def get_queryset(self):
        profile = (
            Profile.objects.get(user=self.request.user))
        queryset = (
            profile.i_like.all()
            .select_related("user")
            .prefetch_related(
                "liked_by__profile", "hashtags"
            )
        )
        return queryset


class IFollowViewSet(PostViewSet, ToggleFollowMixin):
    def get_queryset(self):
        queryset = PostViewSet.get_queryset(self)
        user = self.request.user.profile
        following_profiles = user.is_following.all()
        queryset = queryset.filter(user__in=following_profiles)
        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="toggle-follow",
        permission_classes=[IsAuthenticated],
    )
    def toggle_follow(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        return self.toggle_follow_common(request, post)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = (
        Comment.objects
        .select_related("user", "post__user", "post__user__profile", "parent__user")
        .prefetch_related("replies__user", "replies__post", "replies__parent")
    )
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action == "update" or self.action == "destroy":
            return [IsLoggedIn()]
        if self.action == "reply":
            return [IsAuthenticated()]

        return [IsAuthenticatedReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        if self.action == "retrieve":
            return CommentDetailSerializer
        if self.action == "update":
            return CommentCreateSerializer
        if self.action == "reply":
            return CommentReplySerializer

        return CommentSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="reply",
        permission_classes=[IsAuthenticated],
    )
    def reply(self, request, pk):
        comment = self.get_object()
        user = request.user
        reply = request.data.get("reply", "")

        if request.method == "POST":
            comment = Comment.objects.create(
                post=comment.post, user=user, text=reply, is_reply=True, parent=comment
            )

            serializer = self.get_serializer(comment, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.query_params.get("user")
        text = self.request.query_params.get("text")
        queryset = self.queryset.all()

        if user:
            queryset = queryset.filter(
                Q(user__email__icontains=user)
                | Q(user__first_name__icontains=user)
                | Q(user__last_name__icontains=user)
            )
        if text:
            queryset = queryset.filter(text__icontains=text)

        return queryset.distinct()


