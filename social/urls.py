from django.urls import path, include
from rest_framework import routers

from .views import (
    PostViewSet,
    ProfileViewSet,
    IFollowViewSet,
    CommentViewSet,
    ILikeViewSet,
)

router = routers.DefaultRouter()

router.register("posts", PostViewSet, basename="posts")
router.register("ifollow", IFollowViewSet, basename="ifollow")
router.register("ilike", ILikeViewSet, basename="ilike")
router.register("profiles", ProfileViewSet, basename="profiles")
router.register("comments", CommentViewSet, basename="comments")

urlpatterns = router.urls

app_name = "social"
