from __future__ import absolute_import
import os
from django.test.utils import setup_test_environment
import django
from django.core.management import call_command
import data_wizard

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "tests.settings")
if os.environ.get('CELERY'):
    from .celery import app as celery_app  # noqa

setup_test_environment()
django.setup()
call_command('makemigrations', interactive=False)
call_command('migrate', interactive=False)
print("Using Backend:", data_wizard.backend.__module__)
