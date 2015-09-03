from django.shortcuts import render
from django.core.mail import send_mail
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import mixins
from rest_framework import generics
from api.models import Chore
from rest_auth.serializers import UserSerializer
from rest_auth.models import Profile
from rest_auth.permissions import IsAccountActivated
from api.permissions import IsOwnerOrReadOnly
from django.contrib.auth.models import User
import hashlib, datetime, random
from django.utils import timezone
import logging
# Create your views here.


class Register(APIView):

    def post(self, request, format=None):

        data = request.data
        username = data['username']
        email = data['email']

        random_string = str(random.random()).encode('utf8')

        salt = hashlib.sha1(random_string).hexdigest()[:5]
        salted = (salt + email).encode('utf8')
        activation_key = hashlib.sha1(salted).hexdigest()
        key_expires = datetime.datetime.today() + datetime.timedelta(2)

        data.update({'activation_key':activation_key, 'key_expires':key_expires})

        serializer = UserSerializer(data=data)

        if serializer.is_valid():

            serializer.save()
            # serializer.save(activation_key=activation_key, key_expires=key_expires)

            email_subject = 'HouseMate Account Activation'
            email_body = 'Hey %s, thanks for signing up. To activate your account, click this link within \
                48hours http://127.0.0.1:8000/register/activate/%s' % (username, activation_key)
            send_mail(email_subject, email_body, 'registration@housemate.com', (email,), fail_silently=False)

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUser(APIView):

    def get_profile(self, activation_key):
        try:
            return Profile.objects.get(activation_key=activation_key)
        except Chore.DoesNotExist:
            raise Http404

    def get(self, request, activation_key, format=None):
        profile = self.get_profile(activation_key)

        if profile.key_expires < timezone.now():
            return Response("key expired, a new activation key has been emailed to you")

        profile.account_activated = True
        profile.save()
        return Response(activation_key)


class UserList(APIView):

    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, format=None):

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

