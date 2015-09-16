# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('relate', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetaColumn',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=10, blank=True, choices=[('site', 'Site Metadata'), ('event', 'Event Metadata'), ('report', 'Report Metadata'), ('parameter', 'Parameter Metadata'), ('result', 'Result Data/Metadata')])),
            ],
            options={
                'db_table': 'wq_metacolumn',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Range',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=10, choices=[('head', 'Column header / label'), ('value', 'Global Value'), ('list', 'Data series'), ('row', 'Individual Record')])),
                ('start_row', models.IntegerField()),
                ('end_row', models.IntegerField(null=True, blank=True)),
                ('start_column', models.IntegerField()),
                ('end_column', models.IntegerField()),
                ('relationship', models.ForeignKey(to='relate.Relationship')),
            ],
            options={
                'db_table': 'wq_range',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SkippedRecord',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
            ],
            options={
                'db_table': 'wq_skippedrecord',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnknownItem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'wq_unknownitem',
            },
            bases=(models.Model,),
        ),
    ]
