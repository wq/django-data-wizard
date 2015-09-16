from __future__ import absolute_import

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "tests.settings")

from django.test.utils import setup_test_environment
setup_test_environment()

# Django 1.7
import django
if hasattr(django, 'setup'):
    django.setup()

from .celery import app as celery_app  # noqa

from django.core.management import call_command
call_command('migrate', 'auth', interactive=False)
call_command('migrate', 'files', interactive=False)
call_command('migrate', interactive=False)
