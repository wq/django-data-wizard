import os

TEST_BACKEND = os.environ.get("TEST_BACKEND", "threading")
TEST_VARIANT = os.environ.get("TEST_VARIANT", "default")
WITH_WQDB = TEST_VARIANT == "wq.db"

SECRET_KEY = "1234"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

if TEST_VARIANT == "wq.db":
    WQ_APPS = (
        "wq.db.rest",
        "wq.db.rest.auth",
    )
else:
    WQ_APPS = tuple()

if TEST_VARIANT == "reversion":
    REVERSION_APPS = ("reversion",)
else:
    REVERSION_APPS = tuple()


INSTALLED_APPS = (
    (
        "django.contrib.contenttypes",
        "django.contrib.admin",
        "django.contrib.sessions",
        "django.contrib.staticfiles",
        "django.contrib.auth",
    )
    + WQ_APPS
    + REVERSION_APPS
    + (
        "data_wizard",
        "data_wizard.sources",
        "tests.data_app",
        "tests.naturalkey_app",
        "tests.eav_app",
        "tests.source_app",
    )
)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "data_wizard_test.sqlite3",
    }
}

ROOT_URLCONF = "tests.urls"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "media")

if TEST_BACKEND == "celery":
    CELERY_RESULT_BACKEND = BROKER_URL = "redis://localhost/0"

if TEST_VARIANT == "wq.db":
    from wq.db.default_settings import *  # noqa

DATA_WIZARD = {
    "BACKEND": f"data_wizard.backends.{TEST_BACKEND}",
}

STATIC_URL = "/static/"

DEBUG = True
