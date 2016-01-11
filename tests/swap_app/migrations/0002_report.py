# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('swap_app', '0001_initial'),
        ('auth', '0001_initial'),
        ('vera', '0002_event_report'),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('entered', models.DateTimeField(blank=True)),
                ('event', models.ForeignKey(related_name='report_set', to=settings.WQ_EVENT_MODEL)),
                ('status', models.ForeignKey(blank=True, null=True, to=settings.WQ_REPORTSTATUS_MODEL)),
                ('user', models.ForeignKey(blank=True, related_name='swap_app_record', null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
