from django import template
from metra.models import Direction

register = template.Library()

@register.filter
def direction(value):
    return Direction(value).label