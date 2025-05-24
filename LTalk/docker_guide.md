# Running LTalk with Docker

This guide explains how to run the LTalk application using Docker and Docker Compose.

## Prerequisites
You have to download docker desktop and have it opened so that the conatiner could be run.

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setting up environment variables

1. Create a .env file in the project root:

```sh
# Database configuration
POSTGRES_DB=ltalk_db
POSTGRES_USER=ltalk_user
POSTGRES_PASSWORD=your_secure_password

# Django settings
SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your_domain.com
CSRF_TRUSTED_ORIGINS=http://localhost,https://your_domain.com

# Google API (for Gemini)
GOOGLE_API_KEY=your_google_api_key

# Database connection string (used by Django)
DATABASE_URL=postgres://ltalk_user:your_secure_password@db:5432/ltalk_db
```

## Building and running the application

1. Build the containers:

```sh
docker compose build
```

2. Start the services:

```sh
docker compose up
```

3. Access the application at http://localhost

## Running migrations

When running for the first time or after model changes:

```sh
docker compose exec web python manage.py migrate
```

## Creating a superuser

To create an admin user:

```sh
docker compose exec web python manage.py createsuperuser
```
## Static files

If static files are missing, try:

```sh
docker compose exec web python manage.py collectstatic --no-input
```

## Using the Logging System

LTalk has a comprehensive logging system configured for Docker environments.

### Log Configuration

In Docker, logs are written to:
- Console output (visible in Docker logs)
- File at `/var/log/django-debug.log` inside the container

### Log Levels

The following log levels are available (from least to most severe):
- DEBUG: Detailed debugging information
- INFO: Confirmation that things are working as expected
- WARNING: Indication that something unexpected happened
- ERROR: Serious problem that prevents a function from working
- CRITICAL: Serious error indicating program may be unable to continue

### Using Logger in Code

To use the logger in your code:

```python
import logging
logger = logging.getLogger(__name__)

# Examples:
logger.debug("Detailed information, typically useful for debugging")
logger.info("Confirmation that things are working as expected")
logger.warning("An indication something unexpected happened")
logger.error("A more serious problem that prevents a function from working")
logger.critical("A very serious error that may prevent the program from continuing")
```

### Viewing Logs

View application logs in real-time:

```sh
docker compose logs -f web
```

Access the log file directly inside the container:

```sh
docker compose exec web cat /var/log/django-debug.log
```

Follow the log file in real-time:

```sh
docker compose exec web tail -f /var/log/django-debug.log
```

### Changing Log Levels

To temporarily change log levels for debugging, modify the `LOGGING` configuration in settings_docker.py and restart the services:

```sh
docker compose restart web
```

## Troubleshooting
### Database connection issues

If the web service can't connect to the database, make sure your .env file has the correct database credentials and that the `DATABASE_URL` matches the `POSTGRES_*` values.

### CSRF errors

Check that your `CSRF_TRUSTED_ORIGINS` in the .env file includes the domain you're accessing the site from.

## Docker Compose Commands Reference

- Start services: `docker compose up -d`
- Stop services: `docker compose down`
- View logs: `docker compose logs -f`
- Run command in web container: `docker compose exec web [command]`
- Rebuild containers: `docker compose up -d --build`
