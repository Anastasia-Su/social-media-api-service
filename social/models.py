import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
import os

from django.utils.text import slugify
from rest_framework.exceptions import ValidationError
from users.models import User


class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )

    def __str__(self):
        return f"{self.title} ({self.user})"

    class Meta:
        unique_together = ["title", "description"]


def profile_picture_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.last_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/profile/", filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE,
        null=True,
        unique=True
    )

    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=profile_picture_file_path
    )
    followers = models.ManyToManyField(
        get_user_model(), blank=True, related_name="followers_profile"
    )
    is_following = models.ManyToManyField(
        get_user_model(), blank=True, related_name="is_following_profile"
    )
    # follow = models.BooleanField(default=False)
    FOLLOW_CHOICES = (
        ("F", "Follow"),
        ("U", "Unfollow"),
    )
    follow = models.CharField(max_length=1, choices=FOLLOW_CHOICES)

    # def save(self, *args, **kwargs):
    #     if self.user:
    #         self.first_name = self.user.first_name
    #         self.last_name = self.user.last_name
    #         self.bio = self.user.bio
    #
    #     super(Profile, self).save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({get_user_model().email})"
