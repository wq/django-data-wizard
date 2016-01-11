# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Identifier',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('field', models.CharField(blank=True, max_length=255, null=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('resolved', models.BooleanField(default=False)),
                ('meta', models.TextField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Range',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('row', models.PositiveIntegerField()),
                ('success', models.BooleanField(default=True)),
                ('fail_reason', models.TextField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('template', models.ForeignKey(blank=True, to='data_wizard.Run', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RunLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
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
