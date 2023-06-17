"""
Django settings for Erganiser project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["18.134.135.197", "erganiser.power-10coding.de"]

CSRF_TRUSTED_ORIGINS = ["https://*.power-10coding.de", "http://*.power-10coding.de"]
# Application definition

INSTALLED_APPS = [
    "crispy_forms",
    "users.apps.UsersConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "logbook.apps.LogbookConfig",
    "verify_email.apps.VerifyEmailConfig",
    "whitenoise.runserver_nostatic",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "Erganiser.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "logbook.context_processors.current_month_year",
            ],
        },
    },
]

WSGI_APPLICATION = "Erganiser.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "logbook"),
        "USER": os.environ.get("DB_USER", "test"),
        "PASSWORD": os.environ.get("DB_PASS", "test"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": "5432",
    }
}

# AUTH_USER_MODEL = users.

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
        ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

USE_L10N = False

USE_I18N = True

USE_TZ = True

DATE_INPUT_FORMATS = [
    "%d-%m-%Y",  # '25-10-2006'
    "%d/%m/%Y",  # '25/10/2006'
    "%Y-%m-%d",  # '2006-10-25'
    "%m/%d/%Y",  # '10/25/2006'
    "%m/%d/%y",  # '10/25/06'
    "%b %d %Y",  # 'Oct 25 2006'
    "%b %d, %Y",  # 'Oct 25, 2006'
    "%d %b %Y",  # '25 Oct 2006'
    "%d %b, %Y",  # '25 Oct, 2006'
    "%B %d %Y",  # 'October 25 2006'
    "%B %d, %Y",  # 'October 25, 2006'
    "%d %B %Y",  # '25 October 2006'
    "%d %B, %Y",  # '25 October, 2006'
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_build", "static")
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "Erganiser/static"),
]
CRISPY_TEMPLATE_PACK = "bootstrap4"

LOGIN_REDIRECT_URL = "logbook:index"
LOGIN_URL = "login"

# SMTP Configuration https://github.com/django-ses/django-ses
# TODO: Add in env file
EMAIL_BACKEND = "django_ses.SESBackend"
# These are optional -- if they're set as environment variables they won't
# need to be set here as well
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_SIGNATURE_VERSION = os.environ["AWS_S3_SIGNATURE_VERSION"]
AWS_S3_FILE_OVERWRITE = os.environ["AWS_S3_FILE_OVERWRITE"]
AWS_DEFAULT_ACL = os.environ["AWS_DEFAULT_ACL"]
AWS_S3_VERIFY = os.environ["AWS_S3_VERIFY"]
DEFAULT_FILE_STORAGE = os.environ["DEFAULT_FILE_STORAGE"]


# Additionally, if you are not using the default AWS region of us-east-1,
# you need to specify a region, like so:
AWS_SES_REGION_NAME = os.environ["AWS_SES_REGION_NAME"]

AWS_SES_REGION_ENDPOINT = "email.eu-west-2.amazonaws.com"

DEFAULT_FROM_EMAIL = (
    "rowganiser.power-10coding.de " "<noreply@rowganiser.power-10coding.de>"
)

# If you want to use the SESv2 client
USE_SES_V2 = True

C2_CLIENT_SECRET = os.getenv("C2_CLIENT_SECRET")
C2_CLIENT_ID = os.getenv("C2_CLIENT_ID")

# Django-Verify-Email settings
SUBJECT = "Verify Erganiser Logbook Account"
HTML_MESSAGE_TEMPLATE = "users/email_verification_msg.html"
