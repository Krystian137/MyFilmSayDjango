from django import template
from ..utilis import get_gravatar_url

register = template.Library()

@register.filter
def gravatar_url(email, size=100):
    return get_gravatar_url(email, size)
