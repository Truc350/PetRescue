from django import template

register = template.Library()

@register.filter
def times(number):
    try:
        return range(int(number))
    except:
        return range(0)

@register.filter
def dict_get(d, key):
    try:
        return d.get(int(key), 0)
    except:
        return 0
