from django import template

register = template.Library()


@register.inclusion_tag('utils/input.html')
def get_input(field):
    context = {'field': field}
    return context
