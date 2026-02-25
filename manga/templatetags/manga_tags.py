from django import template

register = template.Library()


@register.filter
def floatformat_int(value):
    """Display integer if whole number, else one decimal."""
    try:
        f = float(value)
        return str(int(f)) if f == int(f) else str(round(f, 1))
    except (TypeError, ValueError):
        return value
