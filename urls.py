__author__ = 'Philip'

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_auth import views

urlpatterns = [
    url(r'^user/$', views.UserDetail.as_view()),
    url(r'^userlist/$', views.UserList.as_view()),
    url(r'^log/$', views.Log.as_view()),
]
