from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_by_route_and_stop(context, route, stop):
    return context["stop_times_by_route_and_stop"][route][stop]