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
import hashlib, datetime, random, uuid
from django.utils import timezone
import logging
# Create your views here.


class Register(APIView):
    """
    Endpoint to register a new user.
    """

    def post(self, request, format=None):
        """
        Creates a new unactivated user and user profile, and sends and email with activation link
        :param request: username, email, password
        :param format:
        :return: Account created message or error 400 - bad request
        """

        data = request.data
        username = data['username']
        email = data['email']
        activation_key = uuid.uuid4()
        key_expires = datetime.datetime.today() + datetime.timedelta(2)

        # Add activation key and key expiry date to data dictionary
        data.update({'activation_key':activation_key, 'key_expires':key_expires})

        serializer = UserSerializer(data=data)

        if serializer.is_valid():

            serializer.save()

            email_subject = 'HouseMate Account Activation'
            email_body = 'Hey %s, thanks for signing up. To activate your account, click this link within \
            48hours http://127.0.0.1:8000/register/activate/%s' % (username, activation_key)
            send_mail(email_subject, email_body, 'registration@housemate.com', (email,), fail_silently=False)

            return Response("Your account has been created. Please check your email for an activation link")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateUser(APIView):
    """
    Endpoint to activate a user
    """

    def get_profile(self, activation_key):
        """
        Gets a user profile based on its activation key
        :param activation_key: the activation key emailed to the user
        :return: user profile object or 404
        """
        try:
            return Profile.objects.get(activation_key=activation_key)
        except Chore.DoesNotExist:
            raise Http404

    def get(self, request, activation_key, format=None):
        """
        Marks the user corresponding to the activation key as active, if it exists
        :param request: None
        :param activation_key: from url emailed to user
        :param format:
        :return: Message confirming activation, resending activation key, or 404
        """
        profile = self.get_profile(activation_key)
        email = profile.user.email
        username = profile.user.username

        if profile.key_expires < timezone.now():
            activation_key = uuid.uuid4()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)
            profile.activation_key = activation_key
            profile.key_expires = key_expires
            profile.save()
            email_subject = 'HouseMate Account Activation'
            email_body = 'Hey %s, thanks for signing up. To activate your account, click this link within ' \
                         '48hours http://127.0.0.1:8000/register/activate/%s' % (username, activation_key)
            send_mail(email_subject, email_body, 'registration@housemate.com', (email,), fail_silently=False)
            return Response("key expired, a new activation key has been emailed to you")

        profile.account_activated = True
        profile.save()
        return Response("Thank you, your account is now active")

class UserDetail(APIView):
    """
    Endpoints to get/update user information, or delete account
    """
    permission_classes = (permissions.IsAuthenticated, IsAccountActivated)

    def get(self, request, format=None):
        """
        Endpoint to get information about the logged in user
        :param request:
        :param format:
        :return:
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, format=None):
        """
        STUB
        :param request:
        :param format:
        :return:
        """
        return Response("STUB")

    def delete(self, request, format=None):
        """
        Endpoint to delete the currently authenticated account
        :param request:
        :param format:
        :return:
        """

class UserList(APIView):

    # permission_classes = (permissions.IsAuthenticated, IsAccountActivated)

    def get(self, request, format=None):

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

