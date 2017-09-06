# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-23 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spatial', '0008_add_history_change_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalspatialrelationship',
            name='created_date',
            field=models.DateTimeField(blank=True, default='2016-01-01 00:00+00', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalspatialrelationship',
            name='last_updated',
            field=models.DateTimeField(blank=True, default='2016-01-01 00:00+00', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalspatialunit',
            name='created_date',
            field=models.DateTimeField(blank=True, default='2016-01-01 00:00+00', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalspatialunit',
            name='last_updated',
            field=models.DateTimeField(blank=True, default='2016-01-01 00:00+00', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='spatialrelationship',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default='2016-01-01 00:00+00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='spatialrelationship',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='spatialunit',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default='2016-01-01 00:00+00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='spatialunit',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
