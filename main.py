from django.conf import settings

from social.tasks import count_posts
import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_media_api_service.settings")

# Initialize Django
django.setup()

def main():
    post_count = count_posts()
    print("Number of posts:", post_count)

if __name__ == "__main__":
    main()