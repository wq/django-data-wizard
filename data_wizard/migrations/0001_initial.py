# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Identifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('field', models.CharField(max_length=255, blank=True, null=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('resolved', models.BooleanField(default=False)),
                ('meta', models.TextField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True, related_name='+')),
            ],
        ),
        migrations.CreateModel(
            name='Range',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=10, choices=[('list', 'Data Column'), ('value', 'Header metadata'), ('data', 'Cell value')])),
                ('header_col', models.IntegerField()),
                ('start_col', models.IntegerField()),
                ('end_col', models.IntegerField(blank=True, null=True)),
                ('header_row', models.IntegerField()),
                ('start_row', models.IntegerField()),
                ('end_row', models.IntegerField(blank=True, null=True)),
                ('count', models.IntegerField(blank=True, null=True)),
                ('identifier', models.ForeignKey(to='data_wizard.Identifier')),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('row', models.PositiveIntegerField()),
                ('success', models.BooleanField(default=True)),
                ('fail_reason', models.TextField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, to='contenttypes.ContentType')),
                ('template', models.ForeignKey(blank=True, null=True, to='data_wizard.Run')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RunLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('event', models.CharField(max_length=100)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('run', models.ForeignKey(to='data_wizard.Run')),
            ],
        ),
        migrations.AddField(
            model_name='record',
            name='run',
            field=models.ForeignKey(to='data_wizard.Run'),
        ),
        migrations.AddField(
            model_name='range',
            name='run',
            field=models.ForeignKey(to='data_wizard.Run'),
        ),
    ]
