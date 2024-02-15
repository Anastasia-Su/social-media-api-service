from django.contrib.auth import get_user_model
from celery import shared_task
from django.db import transaction
from .models import Post


@shared_task
def delay_post_creation(user_id, post_data) -> int | Exception:
    try:
        with transaction.atomic():
            user = get_user_model().objects.get(pk=user_id)
            post = Post.objects.create(
                user=user, **post_data
            )
            return post.id

    except Exception as e:
        return str(e)
