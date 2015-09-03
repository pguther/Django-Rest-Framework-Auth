# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rest_auth', '0004_auto_20150902_2010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='userdescription',
        ),
        migrations.AlterField(
            model_name='profile',
            name='activation_key',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='profile',
            name='key_expires',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 2, 20, 26, 21, 472198)),
        ),
    ]
