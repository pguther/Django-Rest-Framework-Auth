# standard Django imports
from django.db import models
from django.contrib.auth.models import User

# other python imports
import datetime


class Profile(models.Model):
    """
    An extension of the auth.models.User class using a one-to-one relationship. Allows additional fields to be
    associated with the default user
    """
    user = models.OneToOneField(User, unique=True)
    activation_key= models.CharField(max_length=80)
    activation_key_expires = models.DateTimeField(default=datetime.datetime.today())
    account_activated = models.BooleanField(default=False)
    password_recovery_key = models.CharField(max_length=80, blank=True, null=True)
    password_recovery_key_expires = models.DateTimeField(default=datetime.datetime.today())

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural=u'User profiles'
