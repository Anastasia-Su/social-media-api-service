
# Social media API service

API service for social media network, written on DRF.

## Installing / Getting started

Install Postgres and create db.

```shell
git clone https://github.com/Anastasia-Su/social-media-api-service.git
cd social-media-api-service
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt

set SECRET_KEY=<your secret key>
set POSTGRES_HOST=<your host name>
set POSTGRES_DB=<your database>
set POSTGRES_USER=<your usernane>
set POSTGRES_PASSWORD=<your password>
set CELERY_BROKER_URL=<url>
set CELERY_RESULT_BACKEND=<url>

python manage.py migrate
python manage.py runserver
```

## Docker

Docker should be installed.

```shell
docker-compose build
docker-compose up
```

## Celery

To use Celery, uncomment `create` method and comment `perform_create` method in `social > views.py > PostViewSet`.
Set desired countdown.

Set up:
```shell
- docker run -d -p 6379:6379 redis
- celery -A social_media_api_service worker -l INFO -P solo 
```

## Getting access

* Create superuser with profile: type `python manage.py createsuperuser_profile`
* Create users via /api/user/register
* Get access token via /api/user/token
* Refresh tokens via /api/user/token/refresh

## Features

* JWT authentication
* Admin panel: /admin/
* Documentation: api/doc/swagger/ and api/doc/redoc/
* Manage posts and profiles
* Follow users
* Like, dislike and remove likes
* Comment posts and reply to comments
* Add images to your profile and posts
* Filter posts, profiles and comments
* Delay post creation using Celery

## Links

- DockerHub: https://hub.docker.com/repository/docker/anasu888/social-media-api-service/general
