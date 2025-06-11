from django import template
from bs4 import BeautifulSoup

register = template.Library()


@register.inclusion_tag('utils/input.html')
def get_input(field):
    context = {'field': field}
    return context


@register.inclusion_tag('utils/avatar.html')
def get_user_avatar(user_profile, avatar_styles=""):
    context = {'user': user_profile, 'avatar_styles': avatar_styles}
    return context


@register.inclusion_tag('utils/modal.html')
def get_modal(modal_id, title, btn, text=''):
    context = {'modal_id': modal_id, 'title': title, 'text': text, 'btn': btn}
    return context


@register.filter
def strip_tags(html):
    """Remove all HTML tags and return plain text"""
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)  # Convert HTML to plain text
