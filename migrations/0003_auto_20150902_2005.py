# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rest_auth', '0002_auto_20150902_1925'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='userdescription',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='profile',
            name='activation_key',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='profile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 2, 20, 5, 53, 241187)),
        ),
    ]
