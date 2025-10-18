from django.shortcuts import redirect
from django.urls import reverse

def admin_only(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return function(request, *args, **kwargs)
        else:
            return redirect(reverse('get_all_movies'))
    return wrap

def admin_or_moderator_only(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_admin or request.user.is_moderator):
            return function(request, *args, **kwargs)
        else:
            return redirect(reverse('get_all_movies'))
    return wrap
