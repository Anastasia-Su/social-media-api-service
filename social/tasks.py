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
                user=user,
                title=post_data["title"],
                description=post_data["description"],
                hashtags=post_data["hashtags"],
                image=post_data.get("image"),
            )
            post.save()

    except Exception as e:
        return str(e)
