__author__ = 'Philip'

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_auth import views

urlpatterns = [
    url(r'^accounts/register/$', views.Register.as_view()),
    url(r'^accounts/activate/(?P<activation_key>[^/]+)/$', views.ActivateUser.as_view()),
    url(r'^accounts/token/$', views.AuthToken.as_view()),
    url(r'^accounts/user/$', views.UserDetail.as_view()),
    url(r'^accounts/userlist/$', views.UserList.as_view()),
]
