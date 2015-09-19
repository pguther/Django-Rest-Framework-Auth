# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('activation_key', models.CharField(max_length=80)),
                ('activation_key_expires', models.DateTimeField(default=datetime.datetime(2015, 9, 18, 17, 59, 55, 129174))),
                ('account_activated', models.BooleanField(default=False)),
                ('password_recovery_key', models.CharField(null=True, blank=True, max_length=80)),
                ('password_recovery_key_expires', models.DateTimeField(default=datetime.datetime(2015, 9, 18, 17, 59, 55, 129174))),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User profiles',
            },
        ),
    ]
