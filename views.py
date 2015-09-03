from django.shortcuts import render
from django.core.mail import send_mail
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import mixins
from rest_framework import generics
from api.models import Chore
from rest_auth.serializers import UserSerializer, USerializer
from api.permissions import IsOwnerOrReadOnly
from django.contrib.auth.models import User
import hashlib, datetime, random
import logging
# Create your views here.



class UserDetail(APIView):

    def post(self, request, format=None):
        email_subject = 'Test email'
        email_body = 'This is a test email'
        # send_mail(email_subject, email_body, 'tests@housemate.com', ('philip@guther.com',), fail_silently=False)
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():

            username = request.data['username']
            email = request.data['username']

            random_string = str(random.random()).encode('utf8')

            salt = hashlib.sha1(random_string).hexdigest()[:5]
            salted = (salt + email).encode('utf8')
            activation_key = hashlib.sha1(salted).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)

            serializer.save()
            # serializer.save(activation_key=activation_key, key_expires=key_expires)

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Log(APIView):

    def get(self, request, format=None):
        logger = logging.getLogger(__name__)
        logger.debug("==================this is a log message====================")
        return Response('bruh')

class UserList(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

