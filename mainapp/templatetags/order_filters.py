from django import template

register = template.Library()

@register.filter
def filter_pending(orders):
    return [order for order in orders if order.status == 'Pending']

@register.filter
def filter_dispatched(orders):
    return [order for order in orders if order.status == 'Dispatched']

@register.filter
def filter_in_progress(orders):
    progress_statuses = [
        'Fabric Purchased', 'Printing and Dyeing', 
        'Cloth Cutting', 'Stitching', 'Extra Work', 'Finishing and Packing'
    ]
    return [order for order in orders if order.status in progress_statuses]

@register.filter
def filter_by_status(orders, status):
    return [order for order in orders if order.status == status]

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def divide(value, arg):
    if arg:
        return value / arg
    return 0