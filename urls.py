__author__ = 'Philip'

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_auth import views

urlpatterns = [
    url(r'^api/register/$', views.Register.as_view()),
    url(r'^api/userlist/$', views.UserList.as_view()),
    url(r'^register/activate/(?P<activation_key>\w+)/$', views.ActivateUser.as_view()),
]
