"""
Django settings for moushop project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from decouple import config
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

# Paypal keys
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')
PAYPAL_CURRENCY = config('PAYPAL_CURRENCY', default='USD')

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "senecom.onrender.com"]


# Application definition

INSTALLED_APPS = [
    # "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_crontab", # django-crontab
    "dbbackup",  # django-dbbackup"

    "category",
    "accounts",
    "store",
    "carts",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {'location': BASE_DIR / "backup"}

CRONJOBS = [
    ('0 0 * * *', 'moushop.cron.my_scheduled_job')
]


ROOT_URLCONF = "moushop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
          BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "category.context_processors.menu_links",
                "carts.context_processors.counter",
                # Custom context processor for PayPal
                'orders.context_processors.paypal_settings',  
            ],
        },
    },
]

WSGI_APPLICATION = "moushop.wsgi.application"

AUTH_USER_MODEL = "accounts.Account"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
'''
if "RDS_DB_NAME" in os.environ:
    # Database Configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ["RDS_DB_NAME"],
            'USER': os.environ["RDS_USERNAME"],
            'PASSWORD': os.environ["RDS_PASSWORD"],
            'HOST': os.environ["RDS_HOSTNAME"],
            'PORT': os.environ["RDS_PORT"],
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
'''

# Render DATABASE
MODE = config("DEVELOPMENT_MODE", default="development")

if MODE == "development":
    # Use SQLite in development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Use PostgreSQL in production
    DATABASES = {
        "default": dj_database_url.parse(config("DATABASE_URL"))
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

STATICFILES_STORAGES = "whitenoise.storage.CompressedManifestStaticFilesStorage"


STATICFILES_DIRS = [
    BASE_DIR / "moushop/static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Media files configurations
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

# SMTP configuration
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default='localhost')
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")