# Create your tasks here

import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
# from django.core.exceptions import DoesNotExist

from .models import Post


from celery import shared_task

from users.models import User


@shared_task
def count_posts() -> int:
    return Post.objects.count()


@shared_task
def delay_post_creation(user_id, post_data) -> int | Exception:
    try:
        user = User.objects.get(pk=user_id)
        post = Post.objects.create(user=user, **post_data)
        return post.id
    except Exception as e:
        return str(e)
