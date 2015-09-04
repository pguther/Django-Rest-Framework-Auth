__author__ = 'Philip'

from django.forms import widgets
from rest_framework import serializers
from api.models import Chore
from rest_auth.models import Profile
from django.contrib.auth.models import User
import logging


class UserSerializer(serializers.ModelSerializer):
    """
    The serializer for users. Allows account creation, updating, and deletion
    """
    account_activated = serializers.BooleanField(source='profile.account_activated', required=False, read_only=True)
    activation_key = serializers.CharField(source='profile.activation_key', required=False, write_only=True)
    key_expires = serializers.DateTimeField(source='profile.key_expires', required=False, write_only=True)
    password = serializers.CharField(source='user.password', write_only=True)
	
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'account_activated', 'activation_key', 'key_expires',)
        write_only_fields = ('password', 'activation_key', 'key_expires',)
        read_only_fields = ('account_activated',)

    def create(self, validated_data):
        """
        Creates a new user.  Pops off values for user profile, creates the user and userprofile, and associates the two
        Password is added separately to ensure it is correctly hashed
        :param validated_data:
        :return: a newly created user object
        """

        profile_data = validated_data.pop('profile', None)

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        self.create_or_update_profile(user, profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        self.create_or_update_profile(instance, profile_data)
        return super(UserSerializer, self).update(instance, validated_data)

    def create_or_update_profile(self, user, profile_data):
        profile, created = Profile.objects.get_or_create(user=user, defaults=profile_data)
        if not created and profile_data is not None:
            super(UserSerializer, self).update(profile, profile_data)
