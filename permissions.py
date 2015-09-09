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


class IsAuthenticatedOrPostOnly(permissions.BasePermission):
    """
    The request is authenticated as a user, or is a POST only request
    """

    def has_permission(self, request, view):
        return (
            request.method == 'POST' or
            request.user and
            request.user.is_authenticated()
        )