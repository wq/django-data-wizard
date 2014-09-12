# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date', models.DateField()),
            ],
            options={
                'db_table': 'wq_event',
                'ordering': ('-date',),
                'swappable': 'WQ_EVENT_MODEL',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventResult',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('event_date', models.DateField()),
                ('result_value_numeric', models.FloatField(null=True, blank=True)),
                ('result_value_text', models.TextField(null=True, blank=True)),
                ('result_empty', models.BooleanField(default=False)),
                ('event', models.ForeignKey(to=settings.WQ_EVENT_MODEL)),
            ],
            options={
                'db_table': 'wq_eventresult',
                'swappable': 'WQ_EVENTRESULT_MODEL',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('is_numeric', models.BooleanField(default=False)),
                ('units', models.CharField(null=True, max_length=50, blank=True)),
            ],
            options={
                'db_table': 'wq_parameter',
                'ordering': ('name',),
                'swappable': 'WQ_PARAMETER_MODEL',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('entered', models.DateTimeField(blank=True)),
                ('event', models.ForeignKey(to=settings.WQ_EVENT_MODEL)),
            ],
            options={
                'db_table': 'wq_report',
                'ordering': ('-entered',),
                'swappable': 'WQ_REPORT_MODEL',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=255)),
                ('is_valid', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'wq_reportstatus',
                'verbose_name_plural': 'report statuses',
                'swappable': 'WQ_REPORTSTATUS_MODEL',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('value_numeric', models.FloatField(null=True, blank=True)),
                ('value_text', models.TextField(null=True, blank=True)),
                ('empty', models.BooleanField(default=False, db_index=True)),
                ('report', models.ForeignKey(to=settings.WQ_REPORT_MODEL, related_name='results')),
                ('type', models.ForeignKey(to=settings.WQ_PARAMETER_MODEL)),
            ],
            options={
                'ordering': ('type',),
                'db_table': 'wq_result',
                'swappable': 'WQ_RESULT_MODEL',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
            ],
            options={
                'db_table': 'wq_site',
                'swappable': 'WQ_SITE_MODEL',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='site',
            unique_together=set([('latitude', 'longitude')]),
        ),
        migrations.AlterIndexTogether(
            name='result',
            index_together=set([('type', 'report', 'empty')]),
        ),
        migrations.AlterUniqueTogether(
            name='reportstatus',
            unique_together=set([('slug',)]),
        ),
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.ForeignKey(to=settings.WQ_REPORTSTATUS_MODEL, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='report',
            name='user',
            field=models.ForeignKey(related_name='vera_report', to=settings.AUTH_USER_MODEL, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventresult',
            name='event_site',
            field=models.ForeignKey(to=settings.WQ_SITE_MODEL, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result',
            field=models.ForeignKey(to=settings.WQ_RESULT_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result_report',
            field=models.ForeignKey(to=settings.WQ_REPORT_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result_type',
            field=models.ForeignKey(to=settings.WQ_PARAMETER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='eventresult',
            unique_together=set([('event', 'result_type')]),
        ),
        migrations.AddField(
            model_name='event',
            name='site',
            field=models.ForeignKey(to=settings.WQ_SITE_MODEL, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('site', 'date')]),
        ),
    ]
