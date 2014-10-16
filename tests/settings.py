import os

SECRET_KEY = '1234'

MIDDLEWARE_CLASSES = tuple()

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'wq.db.rest',
    'wq.db.rest.auth',
    'wq.db.patterns.identify',
    'wq.db.patterns.relate',
    'wq.db.contrib.files',
    'vera',
    'dbio',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'vera_test',
        'USER': 'postgres',
    }
}

ROOT_URLCONF = "tests.urls"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "media")

WQ_DEFAULT_REPORT_STATUS = 100

CELERY_ALWAYS_EAGER = True
CELERY_RESULT_BACKEND = 'redis://localhost/0'

SWAP = False

from wq.db.rest.settings import *
