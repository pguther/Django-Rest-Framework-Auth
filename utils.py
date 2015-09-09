__author__ = 'Philip'
from django.core.mail import send_mail


def send_activation_email(user):
    email_subject = 'HouseMate Account Activation'
    email_body = 'Hey %s, welcome to HouseMate. To activate your account, click this link within \
    48hours http://127.0.0.1:8000/accounts/activate/%s' % (user.username, user.profile.activation_key)
    send_mail(email_subject, email_body, 'registration@housemate.com', (user.email,), fail_silently=False)
