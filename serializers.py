__author__ = 'Philip'

from django.forms import widgets
from rest_framework import serializers
from api.models import Chore
from rest_auth.models import Profile
from rest_auth.utils import send_activation_email
from django.contrib.auth.models import User
import logging, uuid, datetime

USER_FIELDS = ('username', 'email', 'password', 'first_name', 'last_name')

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user modifiable user information other than password
    """
    account_activated = serializers.BooleanField(source='profile.account_activated', required=False, read_only=True)
    activation_key = serializers.CharField(source='profile.activation_key', required=False, write_only=True)
    key_expires = serializers.DateTimeField(source='profile.key_expires', required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'account_activated', 'activation_key', 'key_expires',)
        write_only_fields = ('activation_key', 'key_expires',)
        read_only_fields = ('account_activated', 'username')

    def update(self, instance, validated_data):

        profile_data = dict()
        user_data = dict()

        for key, value in validated_data.items():
            if key not in USER_FIELDS:
                profile_data.update({key: value})
            else:
                user_data.update({key:value})

        if 'email' in validated_data and validated_data['email'] != instance.email:
            activation_key = uuid.uuid4()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)
            profile_data.update({'activation_key':activation_key, 'key_expires':key_expires, 'account_activated':False})

        self.create_or_update_profile(instance, profile_data)

        for key, value in user_data.items():
            setattr(instance, key, value)

        instance.save()

        if 'email' in validated_data:
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
    key_expires = serializers.DateTimeField(source='profile.key_expires', required=False, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'email', 'account_activated',
                  'activation_key', 'key_expires',)
        write_only_fields = ('password', 'activation_key', 'key_expires',)
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
        key_expires = datetime.datetime.today() + datetime.timedelta(2)

        # Add activation key and key expiry date to data dictionary
        profile_data.update({'activation_key':activation_key, 'key_expires':key_expires})

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
