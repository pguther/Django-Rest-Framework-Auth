# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rest_auth', '0008_auto_20150907_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 7, 20, 24, 51, 733136)),
        ),
    ]
