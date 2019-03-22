from django import template
from datetime import date, timedelta

register = template.Library()
@register.filter(name='multiply')
def multiply(value1, value2):
    return round(value1*value2)
