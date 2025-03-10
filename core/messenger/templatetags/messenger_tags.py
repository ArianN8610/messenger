from django import template
from datetime import datetime, timedelta

from django.contrib.humanize.templatetags.humanize import naturaltime

register = template.Library()


@register.filter
def get_last_message_time_display(message_time):
    """Improve the last message time structure to display"""
    if not message_time:
        return message_time

    today = datetime.today()
    yesterday = (today - timedelta(days=1)).date()

    if message_time.date() == today.date():
        return message_time.strftime("%H:%M")
    elif message_time.date() == yesterday:
        return "yesterday"
    else:
        return message_time.strftime("%m/%d/%Y")


@register.filter
def get_message_time_display(message_datetime):
    """Improve the message time structure to display"""
    today = datetime.today()
    yesterday = (today - timedelta(days=1)).date()
    message_time = message_datetime.strftime("%H:%M")
    time_result = ""

    if message_datetime.date() == today.date():
        time_result = f"{message_time}"
    elif message_datetime.date() == yesterday:
        time_result = f"yesterday {message_time}"
    elif message_datetime.isocalendar()[:2] == today.isocalendar()[:2]:
        time_result = f"{message_datetime.strftime('%a')} {message_time}"

    return time_result


@register.filter
def last_seen_display(last_seen):
    if last_seen.date() == datetime.today().date():
        return 'recently'
    else:
        return naturaltime(last_seen)
