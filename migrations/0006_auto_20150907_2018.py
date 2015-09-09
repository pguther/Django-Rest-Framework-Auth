# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rest_auth', '0005_auto_20150902_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 7, 20, 18, 21, 387578)),
        ),
    ]
