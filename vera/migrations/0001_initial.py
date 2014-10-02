# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swapper


class Migration(migrations.Migration):

    dependencies = [
        swapper.dependency('auth', 'User'),
        swapper.dependency('vera', 'Event'),
        swapper.dependency('vera', 'ReportStatus'),
        swapper.dependency('vera', 'Parameter'),
        swapper.dependency('vera', 'Site'),
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
                'swappable': swapper.swappable_setting('vera', 'Event'),
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
                'swappable': swapper.swappable_setting('vera', 'Parameter'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('entered', models.DateTimeField(blank=True)),
                ('event', models.ForeignKey(to=swapper.get_model_name('vera', 'Event'))),
            ],
            options={
                'db_table': 'wq_report',
                'ordering': ('-entered',),
                'swappable': swapper.swappable_setting('vera', 'Report'),
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
                'swappable': swapper.swappable_setting('vera', 'ReportStatus'),
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
                'swappable': swapper.swappable_setting('vera', 'Site'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='site',
            unique_together=set([('latitude', 'longitude')]),
        ),
        migrations.AlterUniqueTogether(
            name='reportstatus',
            unique_together=set([('slug',)]),
        ),
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.ForeignKey(to=swapper.get_model_name('vera', 'ReportStatus'), null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='report',
            name='user',
            field=models.ForeignKey(related_name='vera_report', to=swapper.get_model_name('auth', 'User'), null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='site',
            field=models.ForeignKey(to=swapper.get_model_name('vera', 'Site'), null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('site', 'date')]),
        ),
    ]
