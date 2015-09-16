# standard django imports
from django.core.mail import send_mail
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.models import User

# django rest framework imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

# rest_auth imports
from rest_auth.serializers import UserSerializer, CreateUserSerializer
from rest_auth.models import Profile
from rest_auth.permissions import IsAccountActivated, IsAuthenticatedOrPostOnly
from rest_auth.utils import send_activation_email

# other imports
import datetime, uuid
# Create your views here.


class AuthToken(ObtainAuthToken):
    """
    Endpoint for authentication token actions
    """

    permission_classes = (IsAuthenticatedOrPostOnly,)

    def post(self, request):
        """
        Returns an authentication token for the username and password pair or bad request
        :param request: username, password
        :return: Authentication token or 400 Bad Request
        """
        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Effectively logs all clients out of the account by replacing the authentication token for the user with
        a new one
        """
        try:
            request.user.auth_token.delete()
        except:
            pass

        return Response("Successfully logged out of all accounts")


class Register(APIView):
    """
    Endpoint to register a new user.
    """

    def post(self, request, format=None):
        """
        Creates a new unactivated user and user profile, and sends and email with activation link
        :param request: username, email, password, first_name, last_name
        :param format:
        :return: Account created message or error 400 - bad request
        """
        serializer = CreateUserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
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
        except Profile.DoesNotExist:
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
            profile.activation_key = uuid.uuid4()
            profile.key_expires = datetime.datetime.today() + datetime.timedelta(2)
            profile.save()
            send_activation_email(profile.user)
            return Response("key expired, a new activation key has been emailed to you")

        profile.account_activated = True
        profile.save()
        return Response("Thank you, your account is now active")


class UserDetail(APIView):
    """
    Endpoints to get/update user information, or delete account
    """
    permission_classes = (permissions.IsAuthenticated, )

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
        user = request.user

        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)

    def delete(self, request, format=None):
        """
        Endpoint to delete the currently authenticated account
        :param request:
        :param format:
        :return:
        """
        return Response("STUB")

class UserList(APIView):

    # permission_classes = (permissions.IsAuthenticated, IsAccountActivated)

    def get(self, request, format=None):

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

