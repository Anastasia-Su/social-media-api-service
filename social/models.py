from django.conf import settings
from django.db import models


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
