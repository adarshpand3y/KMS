from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def get_status_position(status):
    status_positions = {
        'Pending': 1,
        'Fabric Purchased': 2,
        'Printing and Dyeing Sent': 3,
        'Printing and Dyeing Received': 4,
        'Cloth Cutting': 5,
        'Stitching': 6,
        'Extra Work': 7,
        'Finishing and Packing': 8,
        'Dispatched': 9
    }
    return status_positions.get(status, 0)

@register.filter(name='indian_number_format')
def indian_number_format(value):
    """
    Format the number in Indian style (e.g., 1,00,00,000).
    """
    if not isinstance(value, (int, float, Decimal)):
        return value
    try:
        value_str = str(int(value))
        is_negative = value_str.startswith('-')
        if is_negative:
            value_str = value_str[1:]
        length = len(value_str)
        if length <= 3:
            formatted_value = value_str
        else:
            formatted_value = value_str[-3:]
            remaining = value_str[:-3]
            while remaining:
                if len(remaining) >= 2:
                    formatted_value = remaining[-2:] + ',' + formatted_value
                    remaining = remaining[:-2]
                else:
                    formatted_value = remaining + ',' + formatted_value
                    remaining = ''
        if is_negative:
            formatted_value = '-' + formatted_value
        return formatted_value
    except Exception as e:
        return value