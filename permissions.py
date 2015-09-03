__author__ = 'Philip'

from rest_framework import permissions
import logging


class IsAccountActivated(permissions.BasePermission):
    """
    Custom permission to make sure the user's account is activated before it can be used
    """
    def has_permission(self, request, view):

        profile = request.user.profile

        return profile.account_activated is True

