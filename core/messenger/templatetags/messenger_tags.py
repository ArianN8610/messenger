from django import template
from datetime import datetime, timedelta

register = template.Library()


@register.filter
def get_message_time_display(message_time):
    """Improve the message time structure to display"""
    today = datetime.today()
    yesterday = (today - timedelta(days=1)).date()

    if message_time.date() == today.date():
        return message_time.strftime("%H:%M")
    elif message_time.date() == yesterday:
        return "yesterday"
    else:
        return message_time.strftime("%m/%d/%Y")
