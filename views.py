# standard django imports
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import FormView, TemplateView
from django.core.urlresolvers import reverse_lazy

# django rest framework imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

# rest_accounts imports
from rest_accounts.serializers import UserSerializer, CreateUserSerializer, ChangePasswordSerializer, \
    ResetPasswordSerializer
from rest_accounts.models import Profile
from rest_accounts.permissions import IsAuthenticatedOrPostOnly
from rest_accounts.utils import send_activation_email
from rest_accounts.forms import SetPasswordForm

# other imports
import datetime, uuid


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

        if profile.activation_key_expires < timezone.now():
            profile.activation_key = uuid.uuid4()
            profile.activation_key_expires = datetime.datetime.today() + datetime.timedelta(2)
            profile.save()
            send_activation_email(profile.user)
            return Response("key expired, a new activation key has been emailed to you",
                            status=status.HTTP_412_PRECONDITION_FAILED)

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
        :return: Json representation of the account information
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, format=None):
        """
        Endpoint to update user information other than password and username.  If email is updated, account will
        be marked as unactivated and an activation email will be sent to the new email.  Unactivated accounts can only
        access and change their own account information.
        :param request: first_name, last_name, email,
        :param format:
        :return: Json representation of the updated account information
        """
        user = request.user

        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        """
        Endpoint to delete the currently authenticated account
        :param request:
        :param format:
        :return:
        """
        return Response("STUB")


class ChangePassword(APIView):
    """
    Endpoint to change the authenticated user's password
    Auth token WILL be deleted upon a successful password change so a new one needs to be requested
    """
    permission_classes = (permissions.IsAuthenticated, )

    def put(self, request, format=None):
        serializer = ChangePasswordSerializer(request.user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response("Password succesfully changed")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserList(APIView):

    # permission_classes = (permissions.IsAuthenticated, IsAccountActivated)

    def get(self, request, format=None):

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class ResetPassword(APIView):

    def post(self, request, format=None):
        """
        Sends a password reset email to a user email address given a valid username or email
        :param request: username_or_email
        :param format:
        :return:
        """

        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.save()
            return Response("Password recovery email has been sent to %s" % (email))

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirm(FormView):
    template_name = "reset_password_template.html"
    form_class = SetPasswordForm

    def get_success_url(self):
        return reverse_lazy('reset_password_success')

    def get_profile(self, password_recovery_key):
        """
        Gets a user profile based on its password_recovery_key
        :param password_recovery_key: the password recovery key emailed to the user
        :return: user profile object or 404
        """
        try:
            return Profile.objects.get(password_recovery_key=password_recovery_key)
        except Profile.DoesNotExist:
            raise Http404

    def post(self, request, password_recovery_key=None, *arg, **kwargs):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.  If successful, auth tokens will be deleted so all instances
        will need to log in again
        """
        form = self.form_class(request.POST)
        assert password_recovery_key is not None  # checked by URLconf

        profile = self.get_profile(password_recovery_key)

        user = profile.user

        if profile.activation_key_expires >= timezone.now():

            if form.is_valid():
                new_password= form.cleaned_data['new_password2']
                user.set_password(new_password)
                try:
                    user.auth_token.delete()
                except:
                    pass
                user.save()

                messages.success(request, 'Password has been reset.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Password reset was unsuccessful.')
                return self.form_invalid(form)
        else:
            messages.error(request, 'Password recovery key has expired.')
            return self.form_invalid(form)

class ResetPasswordSuccess(TemplateView):
    template_name = "password_reset_success.html"