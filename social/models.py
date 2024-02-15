import uuid
import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager


# class CustomTaggableManager(TaggableManager):
#     def value_from_object(self, instance):
#         value = super().value_from_object(instance)
#         if isinstance(value, str):
#             return value.split(',')
#         return value


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
    FOLLOW_CHOICES = (
        ("F", "Follow"),
        ("U", "Unfollow"),
    )
    follow = models.CharField(max_length=1, choices=FOLLOW_CHOICES)

    i_like = models.ManyToManyField(
        "Post", blank=True, related_name="posts_i_like"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name} ({get_user_model().email})"


def post_picture_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=post_picture_file_path
    )
    hashtags = TaggableManager()
    follow = models.CharField(
        max_length=1,
        choices=Profile.FOLLOW_CHOICES,
        default="U",
    )

    LIKE_CHOICES = (
        ("L", "Like"),
        ("D", "Dislike"),
        ("U", "Unlike"),
    )
    like = models.CharField(max_length=1, choices=LIKE_CHOICES, default="U")
    liked_by = models.ManyToManyField(
        get_user_model(), blank=True, related_name="posts"
    )

    comments = models.ManyToManyField("Comment", blank=True, related_name="posts")

    @property
    def comments_count(self):
        return self.post_comments.count()

    # def __str__(self):
    #     return f"{self.title} ({self.user})"

    class Meta:
        unique_together = ["title", "description"]


class Comment(models.Model):
    text = models.TextField()
    post = models.ForeignKey(
        Post, on_delete=models.PROTECT,
        related_name="post_comments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )
    is_reply = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="comments"
    )
    replies = models.ManyToManyField("Comment", blank=True)

    def __str__(self):
        return self.text


class BlacklistToken(models.Model):
    token = models.CharField(max_length=255)
    blacklisted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token


