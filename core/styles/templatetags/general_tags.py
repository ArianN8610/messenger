from django import template

register = template.Library()


@register.inclusion_tag('utils/input.html')
def get_input(field):
    context = {'field': field}
    return context


@register.inclusion_tag('utils/avatar.html')
def get_user_avatar(user_profile, avatar_styles=""):
    context = {'user': user_profile, 'avatar_styles': avatar_styles}
    return context
