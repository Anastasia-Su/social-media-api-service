from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .mixins import PostMixin, ToggleFollowMixin
from .models import Post, Profile
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
)


class PostViewSet(PostMixin, viewsets.ModelViewSet):
    queryset = Post.objects.select_related("user")
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)


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
        if self.action == "update":
            return [IsLoggedIn()]
        if self.action == "toggle_follow":
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
