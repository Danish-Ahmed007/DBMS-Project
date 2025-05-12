from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='divisibleby')
def divisibleby(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg) if float(arg) else 0
    except (ValueError, TypeError):
        return 0

@register.filter(name='add')
def add(value, arg):
    """Add the arg to the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0
