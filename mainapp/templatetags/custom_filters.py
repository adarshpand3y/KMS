from django import template
from decimal import Decimal
import locale

register = template.Library()

@register.filter
def get_status_position(status):
    status_positions = {
        'Pending': 1,
        'Fabric Purchased': 2,
        'Printing and Dyeing': 3,
        'Cloth Cutting': 4,
        'Stitching': 5,
        'Extra Work': 6,
        'Finishing and Packing': 7,
        'Dispatched': 8
    }
    return status_positions.get(status, 0)

@register.filter(name='indian_number_format')
def indian_number_format(value):
    """
    Format the number in Indian style using the locale module (e.g., 1,00,00,000).
    """
    if not isinstance(value, (int, float, Decimal)):
        print('Not a number', type(value))
        return value

    try:
        # Set the locale to Indian (Hindi)
        locale.setlocale(locale.LC_NUMERIC, 'hi_IN')
        
        # Format the number using locale formatting
        formatted_value = locale.format_string("%d", value, grouping=True)
        
        return formatted_value
    except locale.Error:
        # Fallback in case the locale is not available on the system
        return value