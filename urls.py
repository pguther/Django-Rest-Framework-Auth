__author__ = 'Philip'

from django.conf.urls import url
from rest_accounts import views

urlpatterns = [
    url(r'^register/$', views.Register.as_view()),
    url(r'^activate/(?P<activation_key>[^/]+)/$', views.ActivateUser.as_view()),
    url(r'^token/$', views.AuthToken.as_view()),
    url(r'^user/$', views.UserDetail.as_view()),
    url(r'^userlist/$', views.UserList.as_view()),
    url(r'^password/change/$', views.ChangePassword.as_view()),
    url(r'^password/reset/$', views.ResetPassword.as_view()),
    url(r'^password/reset/confirm/(?P<password_recovery_key>[^/]+)/$', views.ResetPasswordConfirm.as_view(),
        name='reset_password_confirm'),
    url(r'^password/reset/success/$', views.ResetPasswordSuccess.as_view(), name='reset_password_success'),
]
