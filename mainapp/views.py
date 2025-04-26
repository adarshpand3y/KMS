from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDay, TruncMonth
from datetime import datetime, timedelta
from django.contrib.auth.models import User

import random
# from django.utils import timezone

from .models import Order, FabricPurchased, PrintingAndDyeingSent, PrintingAndDyeingReceived, ClothCutting, Stitching, ExtraWork, FinishingAndPacking, Dispatch
from .forms import OrderForm, FabricPurchasedForm, PrintingAndDyeingSentForm, PrintingAndDyeingReceivedForm, ClothCuttingForm, StitchingForm, ExtraWorkForm, FinishingAndPackingForm, DispatchForm

# Create your views here.

# def test(request):
#     orders = Order.objects.all().order_by('-id')
#     fabric_purchased = FabricPurchased.objects.all().order_by('-id')
#     printing_and_dyeing = PrintingAndDyeing.objects.all().order_by('-id')
#     cloth_cutting = ClothCutting.objects.all().order_by('-id')
#     stitching = Stitching.objects.all().order_by('-id')
#     finishing_and_packing = FinishingAndPacking.objects.all().order_by('-id')
#     dispatch = Dispatch.objects.all().order_by('-id')

#     for order in orders:
#         # Set order date to random date this month
#         order.order_date = datetime.now().replace(day=random.randint(1, 28), month=datetime.now().month, year=datetime.now().year)
#         order.save()

#         # Set orderid to random string of length 10
#         order.style_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))
#         order.save()
    
#     for fabric in fabric_purchased:
#         # Set fabric purchased date to random date this month
#         fabric.date = datetime.now().replace(day=random.randint(1, 28), month=datetime.now().month, year=datetime.now().year)
#         fabric.save()
    
#     for printing in printing_and_dyeing:
#         # Set printing and dyeing date to random date this month
#         printing.date = datetime.now().replace(day=random.randint(1, 28), month=datetime.now().month, year=datetime.now().year)
#         printing.save()
    
#     for cloth in cloth_cutting:
#         # Set cloth cutting date to random date this month
#         cloth.date = datetime.now().replace(day=random.randint(1, 28), month=datetime.now().month, year=datetime.now().year)
#         cloth.save()
    
#     for stitch in stitching:
#         # Set stitching date to random date this month
#         stitch.date = datetime.now().replace(day=random.randint(1, 28), month=datetime.now().month, year=datetime.now().year)
#         stitch.save()

#     for finishing in finishing_and_packing:
#         # Set finishing and packing date to random date this month
#         finishing.date = datetime.now().replace(day=random.randint(1, 28), month=datetime.now().month, year=datetime.now().year)
#         finishing.save()
    
#     for dispatch_obj in dispatch:
#         # Set dispatch date to random date this month
#         dispatch_obj.date = datetime.now().replace(day=random.randint(1, 28), month=datetime.now().month, year=datetime.now().year)
#         dispatch_obj.save()

#     return render(request, 'test.html')

@login_required
def index(request):
    # Get the current date and the first day of this month
    today = datetime.today()
    first_day_of_month = today.replace(day=1)

    # Query all the orders for this month
    orders = Order.objects.filter(order_date__gte=first_day_of_month).order_by('-order_date')

    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total_revenue=Sum('amount'))['total_revenue'] or 0
    in_production = Order.objects.exclude(status='Dispatched').count()
    dispatched_orders = Order.objects.filter(status='Dispatched').count()

    # Group the orders by the day of the week (0=Monday, 6=Sunday)
    orders_by_day = orders.annotate(day_of_week=TruncDay('order_date')).values('day_of_week').annotate(count=Count('id')).order_by('day_of_week')

    # Initialize the week days (Sunday=0, Monday=1, ..., Saturday=6)
    week_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Prepare the data for the chart (count per day)
    day_counts = [0] * 7  # List to hold counts for each day of the week
    
    # Adjust the indexing so Sunday is the first day (0) and Monday is the second day (1)
    for order in orders_by_day:
        day_index = order['day_of_week'].weekday()  # 0=Monday, 6=Sunday
        adjusted_day_index = (day_index + 1) % 7  # Shift days, Sunday=0, Monday=1, ..., Saturday=6
        day_counts[adjusted_day_index] = order['count']
    
    week_days_with_counts = [f"{day} ({count})" for day, count in zip(week_days, day_counts)]

    # Get all orders placed in the current month
    start_of_month = today.replace(day=1)
    orders_this_month = Order.objects.filter(order_date__gte=start_of_month)

    # Aggregate the total revenue by day
    revenue_data = (
        orders_this_month
        .values('order_date')  # Group by date
        .annotate(total_revenue=Sum('amount'))  # Sum the amount for each date
        .order_by('order_date')  # Order by date
    )

    # Prepare the data for the chart
    dates = []
    revenues = []
    for data in revenue_data:
        dates.append(data['order_date'].strftime('%Y-%m-%d'))
        revenues.append(data['total_revenue'] or 0)

    # Get all orders placed in the current month
    orders_this_month = Order.objects.filter(order_date__gte=start_of_month)

    # Count the number of orders in each status
    # Annotate the orders with their status and count them
    status_data = (
        orders_this_month
        .values('status')
        .annotate(order_count=Count('id'))
        .order_by('status')
    )
    
    # Prepare data for the chart
    statuses = ["Pending", "Fabric Purchased", "Printing and Dyeing", "Cloth Cutting", "Stitching", "Extra Work", "Finishing and Packing", "Dispatched"]
    order_counts = [0] * len(statuses)
    for data in status_data:
        status_index = statuses.index(data['status'])
        order_counts[status_index] = data['order_count']
    
    # ==================== Pending Duration Chart ====================

    # Get all orders that are not dispatched, and order them by order_date (descending)
    incomplete_orders = Order.objects.exclude(status='Dispatched').order_by('-order_date')[:10]

    # Prepare data for the chart
    order_labels = []
    waiting_times = []

    for order in incomplete_orders:
        # Calculate the waiting time in days
        waiting_days = (today.date() - order.order_date).days
        order_labels.append(f"Order #{order.style_id}")
        waiting_times.append(waiting_days)

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'in_production': in_production,
        'dispatched_orders': dispatched_orders,
        'orders': orders[:20], ## Display only the first 20 orders
        'day_counts': day_counts,
        'week_days': week_days,
        'week_days_with_counts': week_days_with_counts,
        'dates': dates,
        'revenues': revenues,
        'statuses': statuses,
        'order_counts': order_counts,
        'order_labels': order_labels,
        'waiting_time_in_days': waiting_times,
    }
    return render(request, 'index.html', context)

def index2(request):

    # This is index function with additional data fetching and processing
    orders = Order.objects.all().order_by('-order_date')
    
    # Get monthly revenue data
    monthly_revenue = Order.objects.annotate(
        month=TruncMonth('order_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Get top customers by order volume
    top_customers = Order.objects.values('order_received_from').annotate(
        total_quantity=Sum('quantity'),
        order_count=Count('id')
    ).order_by('-total_quantity')[:5]
    
    context = {
        'orders': orders,
        'STATUS': Order.STATUS,
        'monthly_revenue': monthly_revenue,
        'top_customers': top_customers,
    }
    return render(request, 'index2.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate and log in the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('index')

    else:
        if request.user.is_authenticated:
            return redirect('index')

        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    else:
        return redirect('index')

@login_required
def add_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, 'Order added successfully.')
            return redirect('index')
    else:
        form = OrderForm()
    return render(request, 'add_order.html', {'form': form})

@login_required
@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    
    # Get all related process objects (if they exist)
    fabric_purchased = FabricPurchased.objects.filter(order=order).first()
    printing_dyeing_sent = PrintingAndDyeingSent.objects.filter(order=order).first()
    printing_dyeing_received = PrintingAndDyeingReceived.objects.filter(order=order).first()
    cloth_cutting = ClothCutting.objects.filter(order=order).first()
    stitching = Stitching.objects.filter(order=order).first()
    extra_works = ExtraWork.objects.filter(order=order)
    finishing_packing = FinishingAndPacking.objects.filter(order=order).first()
    dispatch = Dispatch.objects.filter(order=order).first()

    if dispatch:
        dispatch.box_details = [item for item in dispatch.box_details.replace("\r", "\n").split("\n") if item.strip() != ""]

    context = {
        'order': order,
        'fabric_purchased': fabric_purchased,
        'printing_dyeing_sent': printing_dyeing_sent,
        'printing_dyeing_received': printing_dyeing_received,
        'cloth_cutting': cloth_cutting, 
        'stitching': stitching,
        'extra_works': extra_works,
        'finishing_packing': finishing_packing,
        'dispatch': dispatch,
    }
    return render(request, 'order_detail.html', context)

@login_required
def add_fabricpurchased(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'Pending':
        messages.error(request, 'Fabric purchased details can only be added to orders with status "Pending".')
        return redirect('orderdetail', id=id)
                        
    if request.method == 'POST':
        form = FabricPurchasedForm(request.POST)
        if form.is_valid():
            fabric_purchased = form.save(commit=False)
            fabric_purchased.order = order
            fabric_purchased.user = request.user
            fabric_purchased.save()
            messages.success(request, 'Fabric purchased details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = FabricPurchasedForm()
    return render(request, 'add_fabricpurchased.html', {'form': form, 'order': order})

@login_required
def add_printinganddyeingsent(request, id):
    order = get_object_or_404(Order, id=id)
    if order.status != 'Fabric Purchased':
        messages.error(request, 'Printing and dyeing sent details can only be added to orders with status "Fabric Purchased".')
        return redirect('orderdetail', id=id)
                       
    if request.method == 'POST':
        form = PrintingAndDyeingSentForm(request.POST)
        if form.is_valid():
            printing_dyeing_sent = form.save(commit=False)
            printing_dyeing_sent.order = order
            printing_dyeing_sent.user = request.user
            printing_dyeing_sent.save()
            messages.success(request, 'Printing and dyeing sent details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = PrintingAndDyeingSentForm()
    return render(request, 'add_printinganddyeingsent.html', {'form': form, 'order': order})

@login_required
def add_printinganddyeingreceived(request, id):
    order = get_object_or_404(Order, id=id)
    if order.status != 'Printing and Dyeing Sent':
        messages.error(request, 'Printing and dyeing received details can only be added to orders with status "Printing and Dyeing Sent".')
        return redirect('orderdetail', id=id)
    
    # Get the related sent record
    printing_dyeing_sent = PrintingAndDyeingSent.objects.filter(order=order).first()
    if not printing_dyeing_sent:
        messages.error(request, 'No printing and dyeing sent record found for this order.')
        return redirect('orderdetail', id=id)
    
    # Check if the sent record is already marked as received
    if printing_dyeing_sent.received:
        messages.error(request, 'Printing and dyeing received details have already been added for this order.')
        return redirect('orderdetail', id=id)
                       
    if request.method == 'POST':
        form = PrintingAndDyeingReceivedForm(request.POST)
        if form.is_valid():
            printing_dyeing_received = form.save(commit=False)
            printing_dyeing_received.order = order
            printing_dyeing_received.printing_and_dyeing_sent = printing_dyeing_sent
            printing_dyeing_received.user = request.user
            printing_dyeing_received.save()
            # Saving the received status in the sent record in this model's save()
            messages.success(request, 'Printing and dyeing received details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = PrintingAndDyeingReceivedForm()
    
    context = {
        'form': form, 
        'order': order,
        'printing_dyeing_sent': printing_dyeing_sent
    }
    return render(request, 'add_printinganddyeingreceived.html', context)

@login_required
def add_clothcutting(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'Printing and Dyeing Received':
        messages.error(request, 'Cloth cutting details can only be added to orders with status "Printing and Dyeing".')
        return redirect('orderdetail', id=id)
    
    if request.method == 'POST':
        form = ClothCuttingForm(request.POST)
        if form.is_valid():
            cloth_cutting = form.save(commit=False)
            cloth_cutting.order = order
            cloth_cutting.user = request.user
            cloth_cutting.save()
            messages.success(request, 'Cloth cutting details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = ClothCuttingForm()
    return render(request, 'add_clothcutting.html', {'form': form, 'order': order})

@login_required
def add_stitching(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'Cloth Cutting':
        messages.error(request, 'Stitching details can only be added to orders with status "Cloth Cutting".')
        return redirect('orderdetail', id=id)
    
    if request.method == 'POST':
        form = StitchingForm(request.POST)
        if form.is_valid():
            stitching = form.save(commit=False)
            stitching.order = order
            stitching.user = request.user
            stitching.save()
            messages.success(request, 'Stitching details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = StitchingForm()
    return render(request, 'add_stitching.html', {'form': form, 'order': order})

@login_required
def add_extrawork(request, id):
    order = get_object_or_404(Order, id=id)

    # if order.status != 'Stitching':
    #     messages.error(request, 'Extra work details can only be added to orders with status "Stitching".')
    #     return redirect('orderdetail', id=id)
    
    if request.method == 'POST':
        form = ExtraWorkForm(request.POST)
        if form.is_valid():
            extra_work = form.save(commit=False)
            extra_work.order = order
            extra_work.user = request.user
            extra_work.save()
            messages.success(request, 'Extra work details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = ExtraWorkForm()
    return render(request, 'add_extrawork.html', {'form': form, 'order': order})

@login_required
def add_finishingandpacking(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'Extra Work':
        messages.error(request, 'Finishing and packing details can only be added to orders with status "Extra Work".')
        return redirect('orderdetail', id=id)
    
    if request.method == 'POST':
        form = FinishingAndPackingForm(request.POST)
        if form.is_valid():
            finishing_packing = form.save(commit=False)
            finishing_packing.order = order
            finishing_packing.user = request.user
            finishing_packing.save()
            messages.success(request, 'Finishing and packing details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = FinishingAndPackingForm()
    return render(request, 'add_finishingandpacking.html', {'form': form, 'order': order})

@login_required
def add_dispatch(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'Finishing and Packing':
        messages.error(request, 'Dispatch details can only be added to orders with status "Finishing and Packing".')
        return redirect('orderdetail', id=id)
    
    if request.method == 'POST':
        form = DispatchForm(request.POST)
        if form.is_valid():
            dispatch = form.save(commit=False)
            dispatch.order = order
            dispatch.user = request.user
            dispatch.save()
            messages.success(request, 'Dispatch details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = DispatchForm()
    return render(request, 'add_dispatch.html', {'form': form, 'order': order})

def filter_by_status(request, status):
    STATUS = {
        'pending': 'Pending',
        'fabric_purchased': 'Fabric Purchased',
        'printing_and_dyeing_sent': 'Printing and Dyeing Sent',
        'printing_and_dyeing_received': 'Printing and Dyeing Received',
        'cloth_cutting': 'Cloth Cutting',
        'stitching': 'Stitching',
        'extra_work': 'Extra Work',
        'finishing_and_packing': 'Finishing and Packing',
        'dispatched': 'Dispatched',
        'all': 'All',
    }
    status = STATUS.get(status.lower(), 'All')
    if status == 'All':
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(status=status)
    
    context = {
        'orders': orders,
        'status': status,
    }
    return render(request, 'filter.html', context)

@login_required
def search_orders(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            search_string = request.POST.get('search_string', '')
            if not search_string or search_string.isspace() or search_string == '':
                messages.error(request, 'Search query cannot be empty.')
                return redirect('index')
            orders = Order.objects.filter(Q(style_id=search_string) |
                                        Q(order_received_from__icontains=search_string)).order_by('-order_date')
            context = {
                'orders': orders,
                'search_string': search_string,
            }
            return render(request, 'search.html', context)
        
        messages.error(request, 'Invalid search request. Please try again.')
        return redirect('index')
    
    else:
        messages.error(request, 'Log into your account to access this page.')
        return redirect('index')

def track_dyers(request):
    return render(request, 'track_dyers.html')