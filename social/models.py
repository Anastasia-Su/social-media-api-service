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

    def save(self, *args, **kwargs):
        if self.user:
            self.first_name = self.user.first_name
            print(self.user.first_name)
            self.last_name = self.user.last_name
            self.bio = self.user.bio

        super(Profile, self).save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        existing_profile = Profile.objects.filter(
            user=self.user
        ).exclude(pk=self.pk).exists()
        if existing_profile:
            raise ValidationError("A profile for this user already exists")

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super(Profile, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({get_user_model().email})"
