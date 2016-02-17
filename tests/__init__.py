from __future__ import absolute_import

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "tests.settings")

from .celery import app as celery_app  # noqa

from django.test.utils import setup_test_environment
setup_test_environment()

import django
django.setup()

from django.core.management import call_command
call_command('migrate', interactive=False)
