from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDay, TruncMonth
from datetime import datetime, date
from django.http import HttpResponse

import calendar
import random
import csv
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
    in_pending = Order.objects.filter(status='Pending').count()
    # total_revenue = Order.objects.aggregate(total_revenue=Sum('amount'))['total_revenue'] or 0
    in_production = Order.objects.exclude(status='Dispatched').count() - in_pending
    dispatched_orders = Order.objects.filter(status='Dispatched').count()

    # Get all orders placed in the current month
    start_of_month = today.replace(day=1)
    orders_this_month = Order.objects.filter(order_date__gte=start_of_month)

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
    statuses = ["Pending", "Fabric Purchased", "Printing and Dyeing Sent", "Printing and Dyeing Received", "Cloth Cutting", "Stitching", "Extra Work", "Finishing and Packing", "Dispatched"]
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
        # 'total_revenue': total_revenue,
        'in_pending': in_pending,
        'in_production': in_production,
        'dispatched_orders': dispatched_orders,
        'orders': orders, # Display all orders
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

    order_size_quantities = [
        ["S", order.quantity_xs],
        ["M", order.quantity_s],
        ["L", order.quantity_m],
        ["XL", order.quantity_l],
        ["2XL", order.quantity_xl],
        ["3XL", order.quantity_3xl],
        ["4XL", order.quantity_4xl],
        ["5XL", order.quantity_5xl],
        ["6XL", order.quantity_6xl],
        ["7XL", order.quantity_7xl],
        ["8XL", order.quantity_8xl],
        ["9XL", order.quantity_9xl],
        ["10XL", order.quantity_10xl]
    ]

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
        'order_size_quantities': order_size_quantities
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
        elif request.method == 'GET':
            print(request.GET)
            search_on= request.GET.get('search_on', '')
            search_string = request.GET.get('search', '')
            print(search_on, search_string)
            if not search_string or search_string.isspace() or search_string == '':
                print("inside")
                messages.error(request, 'Search query cannot be empty.')
                return redirect('track_dyers')
            orders = Order.objects.filter(
                status='Printing and Dyeing Sent',
                printinganddyeingsent__dyer_printer_name__iexact=search_string
            ).order_by('-order_date')
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
    unreceived = (
        PrintingAndDyeingSent.objects
        .filter(received=False)
        .values('dyer_printer_name')
        .annotate(
            total_challans=Count('id'),
            total_quantity=Sum('issued_challan_quantity'),
            total_amount=Sum('amount')
        )
        .order_by('dyer_printer_name')
    )
    return render(request, 'track_dyers.html', {'unreceived': unreceived})

@login_required
def export_orders_csv(request, timespan):
    """
    Export orders as CSV based on timespan parameter:
    - 'y': current financial year (April 1 to March 31)
    - 'm': current month
    
    Multiple ExtraWork entries are added at the end of each row.
    """

    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('index')

    # Validate timespan parameter
    if timespan not in ['y', 'm']:
        return HttpResponse("Invalid timespan parameter. Use 'y' for yearly or 'm' for monthly.", status=400)
    
    # Calculate date range based on timespan
    today = date.today()
    
    if timespan == 'y':
        # Financial year (April 1 to March 31)
        if today.month < 4:  # Jan-March
            start_date = date(today.year - 1, 4, 1)
            end_date = date(today.year, 3, 31)
        else:  # April-Dec
            start_date = date(today.year, 4, 1)
            end_date = date(today.year + 1, 3, 31)
    else:  # timespan == 'm'
        # Current month
        start_date = date(today.year, today.month, 1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = date(today.year, today.month, last_day)
    
    # Filter orders based on date range
    orders = Order.objects.filter(
        order_date__gte=start_date,
        order_date__lte=end_date
    ).order_by('order_date')
    
    # Find the maximum number of ExtraWork entries for any order
    max_extra_works = 0
    for order in orders:
        extra_works_count = ExtraWork.objects.filter(order=order).count()
        if extra_works_count > max_extra_works:
            max_extra_works = extra_works_count
    
    # Create HTTP response with CSV file
    response = HttpResponse(content_type='text/csv')
    filename = f"orders_{timespan}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Create CSV writer
    writer = csv.writer(response)
    
    # Base header (without ExtraWork)
    base_header = [
        'Order ID', 'Style ID', 'Order Date', 'Order From', 'Quantity', 'Rate', 'Size', 'Status', 'Amount',
        
        # Fabric Purchased fields
        'Fabric Purchase Date', 'Purchased From', 'Fabric Quantity', 'Fabric Rate', 'Fabric Amount',
        'Invoice Number', 'Fabric Detail', 'Fabric Length', 'Fabric Dyer', 'Challan Number',
        'Issued Challan Date', 'Issued Challan Quantity', 'Balance Fabric',
        
        # Printing & Dyeing Sent fields
        'P&D Sent Date', 'Dyer/Printer Name', 'P&D Fabric Detail', 'P&D Fabric Length',
        'P&D Issued Quantity', 'P&D Received Status', 'P&D Rate', 'P&D Amount',
        
        # Printing & Dyeing Received fields
        'P&D Received Date', 'Shrinkage (%)', 'P&D Received Quantity', 
        'P&D Balance Quantity', 'P&D Received Challan',
        
        # Cloth Cutting fields
        'Cutting Issued Date', 'Cutting Challan', 'Cutting Worker Name', 'Cutting Fabric Detail',
        'Cutting Fabric Length', 'Cutting Issued Quantity', 'Cutting Received Quantity',
        'Cutting Balance', 'Cutting Received Date', 'Cutting Received Challan', 'Cutting Rate', 'Cutting Amount',
        
        # Stitching fields
        'Stitching Issued Date', 'Stitching Challan', 'Stitching Worker Name', 'Stitching Issued Quantity',
        'Stitching Received Quantity', 'Stitching Balance', 'Stitching Received Date', 
        'Stitching Rate', 'Stitching Amount',
        
        # Finishing & Packing fields
        'F&P Issued Date', 'F&P Challan', 'F&P Worker Name', 'F&P Issued Quantity',
        'F&P Packed Quantity', 'F&P Rejected', 'F&P Rate', 'F&P Amount',
        
        # Dispatch fields
        'Dispatch Date', 'Dispatched To', 'Dispatch Quantity', 'Delivery Note',
        'Invoice Number', 'Box Details',
    ]
    
    # Add ExtraWork headers at the end
    extra_work_headers = []
    for i in range(1, max_extra_works + 1):
        extra_work_headers.extend([
            f'Extra Work {i} Issued Date', 
            f'Extra Work {i} Challan', 
            f'Extra Work {i} Worker Name', 
            f'Extra Work {i} Type',
            f'Extra Work {i} Issued Qty', 
            f'Extra Work {i} Received Qty', 
            f'Extra Work {i} Balance',
            f'Extra Work {i} Rate', 
            f'Extra Work {i} Amount', 
            f'Extra Work {i} Received Date'
        ])
    
    # Complete header
    header = base_header + extra_work_headers
    writer.writerow(header)
    
    # Write data rows
    for order in orders:
        # Get related objects
        try:
            fabric = FabricPurchased.objects.filter(order=order).first()
        except FabricPurchased.DoesNotExist:
            fabric = None
            
        try:
            pd_sent = PrintingAndDyeingSent.objects.filter(order=order).first()
        except PrintingAndDyeingSent.DoesNotExist:
            pd_sent = None
            
        try:
            pd_received = PrintingAndDyeingReceived.objects.filter(order=order).first() 
        except PrintingAndDyeingReceived.DoesNotExist:
            pd_received = None
            
        try:
            cutting = ClothCutting.objects.filter(order=order).first()
        except ClothCutting.DoesNotExist:
            cutting = None
            
        try:
            stitching = Stitching.objects.filter(order=order).first()
        except Stitching.DoesNotExist:
            stitching = None
            
        try:
            finishing = FinishingAndPacking.objects.filter(order=order).first()
        except FinishingAndPacking.DoesNotExist:
            finishing = None
            
        try:
            dispatch = Dispatch.objects.filter(order=order).first()
        except Dispatch.DoesNotExist:
            dispatch = None
        
        # Base row (without ExtraWork)
        base_row = [
            order.id, order.style_id, order.order_date, order.order_received_from,
            order.quantity, order.rate, order.size, order.status, order.amount,
            
            # Fabric Purchased fields
            fabric.fabric_purchase_date if fabric else '',
            fabric.purchased_from if fabric else '',
            fabric.quantity if fabric else '',
            fabric.rate if fabric else '',
            fabric.amount if fabric else '',
            fabric.invoice_number if fabric else '',
            fabric.fabric_detail if fabric else '',
            fabric.fabric_length if fabric else '',
            fabric.fabric_dyer if fabric else '',
            fabric.challan_number if fabric else '',
            fabric.issued_challan_date if fabric else '',
            fabric.issued_challan_quantity if fabric else '',
            fabric.balance_fabric if fabric else '',
            
            # Printing & Dyeing Sent fields
            pd_sent.issued_challan_date if pd_sent else '',
            pd_sent.dyer_printer_name if pd_sent else '',
            pd_sent.fabric_detail if pd_sent else '',
            pd_sent.fabric_length if pd_sent else '',
            pd_sent.issued_challan_quantity if pd_sent else '',
            pd_sent.received if pd_sent else '',
            pd_sent.rate if pd_sent else '',
            pd_sent.amount if pd_sent else '',
            
            # Printing & Dyeing Received fields
            pd_received.received_date if pd_received else '',
            pd_received.shrinkage_in_percentage if pd_received else '',
            pd_received.received_quantity if pd_received else '',
            pd_received.balance_quantity if pd_received else '',
            pd_received.received_challan_number if pd_received else '',
            
            # Cloth Cutting fields
            cutting.issued_challan_date if cutting else '',
            cutting.issued_challan_number if cutting else '',
            cutting.job_worker_name if cutting else '',
            cutting.fabric_detail if cutting else '',
            cutting.fabric_length if cutting else '',
            cutting.issued_challan_quantity if cutting else '',
            cutting.received_quantity if cutting else '',
            cutting.balance_quantity if cutting else '',
            cutting.received_date if cutting else '',
            cutting.received_challan_number if cutting else '',
            cutting.rate if cutting else '',
            cutting.amount if cutting else '',
            
            # Stitching fields
            stitching.issued_challan_date if stitching else '',
            stitching.issued_challan_number if stitching else '',
            stitching.job_worker_name if stitching else '',
            stitching.issued_challan_quantity if stitching else '',
            stitching.received_quantity if stitching else '',
            stitching.balance_quantity if stitching else '',
            stitching.received_date if stitching else '',
            stitching.rate if stitching else '',
            stitching.amount if stitching else '',
            
            # Finishing & Packing fields
            finishing.issued_challan_date if finishing else '',
            finishing.issued_challan_number if finishing else '',
            finishing.job_worker_name if finishing else '',
            finishing.issued_challan_quantity if finishing else '',
            finishing.packed_quantity if finishing else '',
            finishing.rejected if finishing else '',
            finishing.rate if finishing else '',
            finishing.amount if finishing else '',
            
            # Dispatch fields
            dispatch.dispatch_date if dispatch else '',
            dispatch.dispatched_to if dispatch else '',
            dispatch.quantity if dispatch else '',
            dispatch.delivery_note if dispatch else '',
            dispatch.invoice_number if dispatch else '',
            dispatch.box_details if dispatch else '',
        ]
        
        # Get all ExtraWork items for this order
        extra_works = ExtraWork.objects.filter(order=order).order_by('id')
        
        # Add ExtraWork data
        extra_work_data = []
        for i in range(max_extra_works):
            if i < len(extra_works):
                work = extra_works[i]
                extra_work_data.extend([
                    work.issued_challan_date,
                    work.issued_challan_number,
                    work.job_worker_name,
                    work.extra_work_name,
                    work.issued_challan_quantity,
                    work.received_quantity,
                    work.balance_quantity,
                    work.rate,
                    work.amount,
                    work.received_date
                ])
            else:
                # Add empty fields for orders with fewer ExtraWork entries
                extra_work_data.extend([''] * 10)  # 10 fields per ExtraWork
        
        # Complete row
        row = base_row + extra_work_data
        writer.writerow(row)
    
    return response