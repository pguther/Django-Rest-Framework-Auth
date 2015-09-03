# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rest_auth', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='userdescription',
        ),
        migrations.AddField(
            model_name='profile',
            name='account_activated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='activation_key',
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name='profile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 2, 19, 25, 39, 214216)),
        ),
    ]
