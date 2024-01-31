from django.db.models import Q, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Post, Profile
from .permissions import (
    IsLoggedIn,
    IsAdminOrIfAuthenticatedReadOnly,
    IsAuthenticatedReadOnly,
)

from .serializers import (
    PostSerializer,
    PostListSerializer,
    ProfileSerializer,
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileImageSerializer,
    FollowActionSerializer,
    # FollowListSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("user")
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileViewSet(viewsets.ModelViewSet):
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

    def get_queryset(self):
        user = self.request.query_params.get("user")
        queryset = self.queryset.all()

        if user:
            queryset = queryset.filter(
                Q(user__email__icontains=user)
                | Q(first_name__icontains=user)
                | Q(last_name__icontains=user)
            )

        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="toggle-follow",
        permission_classes=[IsAuthenticated],
    )
    def toggle_follow(self, request, pk):
        profile = get_object_or_404(Profile, pk=pk)

        if request.method == "POST" and request.user.profile != profile:
            follow_status = request.data.get("follow", "")
            if follow_status == "U":
                profile.followers.remove(request.user)
                request.user.profile.is_following.remove(profile.user)
            if follow_status == "F":
                profile.followers.add(request.user)
                request.user.profile.is_following.add(profile.user)

            profile.save()

            serializer = self.get_serializer(profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)
