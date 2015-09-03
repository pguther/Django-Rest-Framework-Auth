# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rest_auth', '0003_auto_20150902_2005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='activation_key',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='profile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 2, 20, 10, 17, 957616)),
        ),
    ]
