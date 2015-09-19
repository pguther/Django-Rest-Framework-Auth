__author__ = 'Philip'
# standard django imports
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.query_utils import Q

# django rest framework imports
from rest_framework import serializers

# rest_auth imports
from rest_accounts.models import Profile
from rest_accounts.utils import send_activation_email, send_recovery_email

# other python imports
import logging, uuid, datetime

USER_FIELDS = ('username', 'email', 'password', 'first_name', 'last_name')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user modifiable user information other than password
    """
    account_activated = serializers.BooleanField(source='profile.account_activated', required=False, read_only=True)
    activation_key = serializers.CharField(source='profile.activation_key', required=False, write_only=True)
    activation_key_expires = serializers.DateTimeField(source='profile.activation_key_expires', required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'account_activated', 'activation_key',
                  'activation_key_expires')
        write_only_fields = ('activation_key', 'activation_key_expires',)
        read_only_fields = ('account_activated', 'username')

    def update(self, instance, validated_data):

        profile_data = dict()
        user_data = dict()
        send_new_activation = False

        for key, value in validated_data.items():
            if key not in USER_FIELDS:
                profile_data.update({key: value})
            else:
                user_data.update({key:value})

        if 'email' in validated_data and validated_data['email'] != instance.email:
            send_new_activation = True
            activation_key = uuid.uuid4()
            activation_key_expires = datetime.datetime.today() + datetime.timedelta(2)
            profile_data.update({'activation_key':activation_key, 'activation_key_expires':activation_key_expires,
                                 'account_activated':False})

        self.create_or_update_profile(instance, profile_data)

        for key, value in user_data.items():
            setattr(instance, key, value)

        instance.save()

        if send_new_activation:
            send_activation_email(instance)

        return instance

    def create_or_update_profile(self, user, profile_data):
        profile, created = Profile.objects.get_or_create(user=user, defaults=profile_data)
        if not created and profile_data is not None:
            super(UserSerializer, self).update(profile, profile_data)


class CreateUserSerializer(serializers.ModelSerializer):
    """
    The serializer for creating users.
    """
    account_activated = serializers.BooleanField(source='profile.account_activated', required=False, read_only=True)
    activation_key = serializers.CharField(source='profile.activation_key', required=False, write_only=True)
    activation_key_expires = serializers.DateTimeField(source='profile.activation_key_expires', required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'email', 'account_activated',
                  'activation_key', 'activation_key_expires',)
        write_only_fields = ('password', 'activation_key', 'activation_key_expires',)
        read_only_fields = ('account_activated',)

    def create(self, validated_data):
        """
        Creates a new user.  Pops off values for user profile, creates the user and userprofile, and associates the two
        Password is added separately to ensure it is correctly hashed
        :param validated_data:
        :return: a newly created user object
        """

        profile_data = dict()

        for key, value in validated_data.items():
            if key not in USER_FIELDS:
                profile_data.update({key: value})

        activation_key = uuid.uuid4()
        activation_key_expires = datetime.datetime.today() + datetime.timedelta(2)

        # Add activation key and key expiry date to data dictionary
        profile_data.update({'activation_key':activation_key, 'activation_key_expires':activation_key_expires})

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()
        self.create_or_update_profile(user, profile_data)
        send_activation_email(user)
        return user

    def create_or_update_profile(self, user, profile_data):
        profile, created = Profile.objects.get_or_create(user=user, defaults=profile_data)
        if not created and profile_data is not None:
            super(CreateUserSerializer, self).update(profile, profile_data)


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    confirm_new_password = serializers.CharField(max_length=128)

    def __init__(self, *args, **kwargs):
        super(ChangePasswordSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate(self, attrs):

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

        if not self.user.check_password(attrs['old_password']):
            raise serializers.ValidationError("password is incorrect")

        if attrs['confirm_new_password'] != attrs['new_password']:
            raise serializers.ValidationError("new passwords don't match")

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        try:
            instance.auth_token.delete()
        except:
            pass
        instance.save()
        return instance


class ResetPasswordSerializer(serializers.Serializer):

    username_or_email = serializers.CharField(max_length=128)

    def validate_email(self, email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def validate(self, attrs):

        username_or_email = attrs['username_or_email']

        if self.validate_email(username_or_email):
            associated_users = User.objects.filter(Q(email=username_or_email) | Q(username=username_or_email))
            if associated_users.exists():
                return attrs
            else:
                raise serializers.ValidationError("no accounts associated with this email address")
        else:
            associated_users= User.objects.filter(username=username_or_email)
            if associated_users.exists():
                return attrs
            else:
                raise serializers.ValidationError("no account associated with this username")

    def save(self):

        username_or_email = self.validated_data['username_or_email']
        associated_users = User.objects.filter(Q(email=username_or_email) | Q(username=username_or_email))
        email = None
        if associated_users.exists():

            for user in associated_users:
                email = user.email
                profile = user.profile

                profile.password_recovery_key = uuid.uuid4()
                profile.password_recovery_key_expires = datetime.datetime.today() + datetime.timedelta(hours=1)
                profile.save()
                send_recovery_email(user)

        return email

