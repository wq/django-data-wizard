# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swapper


class Migration(migrations.Migration):

    dependencies = [
        ('vera', '0001_initial'),
        swapper.dependency('vera', 'Event'),
        swapper.dependency('vera', 'Report'),
        swapper.dependency('vera', 'Parameter'),
        swapper.dependency('vera', 'Result'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventResult',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('event_date', models.DateField()),
                ('result_value_numeric', models.FloatField(null=True, blank=True)),
                ('result_value_text', models.TextField(null=True, blank=True)),
                ('result_empty', models.BooleanField(default=False)),
                ('event', models.ForeignKey(to=swapper.get_model_name('vera', 'Event'))),
            ],
            options={
                'db_table': 'wq_eventresult',
                'swappable': swapper.swappable_setting('vera', 'EventResult'),
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
                ('report', models.ForeignKey(to=swapper.get_model_name('vera', 'Report'), related_name='results')),
                ('type', models.ForeignKey(to=swapper.get_model_name('vera', 'Parameter'))),
            ],
            options={
                'ordering': ('type',),
                'db_table': 'wq_result',
                'swappable': swapper.swappable_setting('vera', 'Result'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='result',
            index_together=set([('type', 'report', 'empty')]),
        ),
        migrations.AddField(
            model_name='eventresult',
            name='event_site',
            field=models.ForeignKey(to=swapper.get_model_name('vera', 'Site'), null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result',
            field=models.ForeignKey(to=swapper.get_model_name('vera', 'Result')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result_report',
            field=models.ForeignKey(to=swapper.get_model_name('vera', 'Report')),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventresult',
            name='result_type',
            field=models.ForeignKey(to=swapper.get_model_name('vera', 'Parameter')),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='eventresult',
            unique_together=set([('event', 'result_type')]),
        ),
    ]
