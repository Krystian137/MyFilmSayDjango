from django.core.exceptions import PermissionDenied
from functools import wraps
import hashlib

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


def get_gravatar_url(email, size=100):
    email_hash = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=identicon"
