from django.urls import path, include
from rest_framework import routers

from .views import (
    PostViewSet,
    ProfileViewSet,
    # MyProfileViewSet
)

router = routers.DefaultRouter()

router.register("posts", PostViewSet)
router.register("profiles", ProfileViewSet)
# router.register("my-profile", MyProfileViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "social"
