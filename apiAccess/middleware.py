"""
Custom middleware to ensure user data is always fresh from the database.

This middleware addresses an issue where Django's session authentication
could cache stale user objects in memory, causing user data (like expenses)
to not appear after a logout/login cycle.
"""

from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin


class RefreshUserMiddleware(MiddlewareMixin):
    """
    Refreshes the request.user object from the database on each request.
    
    This ensures that user data is always up-to-date and prevents issues
    where a user's data wouldn't appear after logging out and logging back in.
    """
    
    def process_request(self, request):
        """
        Refresh the authenticated user from the database to ensure fresh data.
        """
        # Only refresh if user is authenticated and is not AnonymousUser
        if request.user.is_authenticated:
            try:
                # Refresh the user object from the database to ensure it's not stale
                request.user = User.objects.get(pk=request.user.pk)
            except User.DoesNotExist:
                # If the user doesn't exist anymore, they will be logged out
                from django.contrib.auth import logout
                logout(request)
        
        return None
