from django.db.models import Q
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
    FollowActionSerializer,
    PostDetailSerializer,
    FollowPostActionSerializer
)


class ToggleFollowMixin:
    def toggle_follow_common(self, request, instance=None):
        profile = instance.user.profile

        if request.method == "POST" and request.user.profile != profile:
            follow_status = request.data.get("follow", "")
            if follow_status == "U":
                profile.followers.remove(request.user)
                request.user.profile.is_following.remove(profile.user)
            if follow_status == "F":
                profile.followers.add(request.user)
                request.user.profile.is_following.add(profile.user)

            profile.save()

            serializer = self.get_serializer(instance=profile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)


class PostMixin:
    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action == "toggle_follow":
            return FollowPostActionSerializer

        return PostSerializer

    def get_permissions(self):
        if self.action == "update":
            return [IsLoggedIn()]

        if self.action in ["list", "create", "toggle_follow"]:
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
