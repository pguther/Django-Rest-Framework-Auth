from django.db import models
from django.contrib.auth.models import User
import datetime
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User)
    userdescription = models.TextField(default='', blank=True)
    '''
    activation_key= models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=datetime.datetime.today())
    '''''

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural=u'User profiles'
