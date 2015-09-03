__author__ = 'Philip'

from django.forms import widgets
from rest_framework import serializers
from api.models import Chore
from rest_auth.models import Profile
from django.contrib.auth.models import User
import logging


class UserSerializer(serializers.ModelSerializer):
    userdescription = serializers.CharField(source='profile.userdescription', allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'userdescription',)
        write_only_fields = ('password',)

    def create(self, validated_data):
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

class USerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username',)





'''
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    password = serializers.CharField(source='user.password')
    userdescription = serializers.Field(source='userdescription')

    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'password', 'userdescription',)

    def restore_object(self, validated_data, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            instance.user.email = validated_data.get('user.email', instance.user.email)
            instance.userdescription = validated_data.get('userdescription', instance.userdescription)
            instance.user.password = validated_data.get('user.password', instance.user.password)
            return instance

        user = User.objects.create_user(username=validated_data.get('user.username'), email= validated_data.get('user.email'), password=validated_data.get('user.password'))
        return UserProfile(user=user)





class UserSerializer(serializers.ModelSerializer):
    chores = serializers.PrimaryKeyRelatedField(many=True, queryset=Chore.objects.all, required=False)
    id = serializers.IntegerField(source = 'pk', read_only = True)
    username = serializers.CharField(source = 'user.username', read_only = True)
    email = serializers.CharField(source = 'user.email')
    password = serializers.CharField(source= 'user.password')

    class Meta:
        model=UserProfile
        fields = ('id', 'password', 'username', 'email', 'activation_key', 'key_expires', 'chores')
        write_only_fields = ['password',]

    def create(self, validated_data):
        user = User(email=validated_data['email'], username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()

        newprofile = UserProfile(user=user, activation_key = validated_data['activation_key'],
                                 key_expires = validated_data['key_expires'])
        newprofile.save()
        return newprofile
'''