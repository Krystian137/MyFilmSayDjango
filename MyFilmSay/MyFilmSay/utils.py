from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            raise PermissionDenied()
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_or_moderator_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_admin() or request.user.is_moderator()):
            raise PermissionDenied()
        return view_func(request, *args, **kwargs)
    return _wrapped_view
