from django.urls import path, include
from rest_framework import routers

from .views import (
    PostViewSet,
    ProfileViewSet,
)

router = routers.DefaultRouter()

router.register("posts", PostViewSet)
router.register("profiles", ProfileViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "social"
