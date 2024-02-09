from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .mixins import PostMixin, ToggleFollowMixin
from .models import Post, Profile, Comment
from .permissions import (
    IsLoggedIn,
    IsAdminOrIfAuthenticatedReadOnly,
    IsAuthenticatedReadOnly,
)

from .serializers import (
    PostSerializer,
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
from users.models import User


class PostViewSet(PostMixin, viewsets.ModelViewSet):
    queryset = Post.objects.select_related("user")
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

        if request.method == "POST" and request.user.profile != post.user.profile:
            like_status = request.data.get("like", "")
            if like_status == "U":
                post.liked_by.remove(request.user)
                request.user.profile.i_like.remove(post)
            if like_status in ["L", "D"]:
                post.liked_by.add(request.user)
                request.user.profile.i_like.add(post)

            post.save()

            serializer = self.get_serializer(instance=post, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)

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


class ProfileViewSet(viewsets.ModelViewSet, ToggleFollowMixin):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedReadOnly,)

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
        if self.action == "toggle_follow":
            return [IsAuthenticated()]
        if self.action == "toggle_like":
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

    @action(
        methods=["POST"],
        detail=True,
        url_path="toggle-follow",
        permission_classes=[IsAuthenticated],
    )
    def toggle_follow(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)
        return self.toggle_follow_common(request, profile)


class IFollowViewSet(PostViewSet, ToggleFollowMixin, PostMixin):
    def get_queryset(self):
        queryset = PostMixin.get_queryset(self)
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


class ILikeViewSet(PostViewSet, PostMixin, ProfileViewSet):
    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        queryset = profile.i_like.all()
        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="toggle-like",
        permission_classes=[IsAuthenticated],
    )
    def toggle_like(self, request, pk):
        post = self.get_object()

        if request.method == "POST" and request.user.profile != post.user.profile:
            like_status = request.data.get("like", "")
            if like_status == "U":
                post.liked_by.remove(request.user)
                request.user.profile.i_like.remove(post)
            if like_status in ["L", "D"]:
                post.liked_by.add(request.user)
                request.user.profile.i_like.add(post)

            post.save()

            serializer = self.get_serializer(instance=post, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
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


