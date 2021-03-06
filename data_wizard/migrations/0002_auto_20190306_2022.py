# Generated by Django 2.1.7 on 2019-03-06 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_wizard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='run',
            name='template',
        ),
        migrations.AddField(
            model_name='identifier',
            name='attr_field',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='EAV attribute field'),
        ),
        migrations.AlterField(
            model_name='identifier',
            name='attr_id',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='EAV attribute id'),
        ),
        migrations.AlterField(
            model_name='identifier',
            name='field',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='serializer field'),
        ),
        migrations.AlterField(
            model_name='identifier',
            name='name',
            field=models.CharField(max_length=255, verbose_name='spreadsheet value'),
        ),
        migrations.AlterField(
            model_name='identifier',
            name='value',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='mapped value'),
        ),
        migrations.AlterField(
            model_name='run',
            name='loader',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
