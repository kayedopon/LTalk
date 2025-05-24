from .settings import *  # Import base settings

from pathlib import Path
import os
import dj_database_url     # pip install dj-database-url

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# --- Database (PostgreSQL) ---
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",      # e.g. postgres://user:pass@db:5432/mydb
            "postgres://postgres:postgres@db:5432/postgres"
        ),
        conn_max_age=600,
    )
}

# --- Static files ---
STATIC_URL  = "/static/"
STATIC_ROOT = "/static" 

# # If you keep custom assets within project:
# STATICFILES_DIRS = [
#     BASE_DIR / "main" / "static",
#     BASE_DIR / "authentication" / "static",
    
# ]

# --- Media files (optional) ---
MEDIA_URL = "/media/"
MEDIA_ROOT = Path("/media")

# --- Security & other prod settings ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
# SECRET_KEY should come from environment!
SECRET_KEY = os.getenv("SECRET_KEY")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django-debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'api': {  # Add loggers for your specific apps
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'main': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}