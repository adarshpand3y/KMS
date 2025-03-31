from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

from .models import Order, FabricPurchased, PrintingAndDyeing, ClothCutting, Stitching, FinishingAndPacking, Dispatch
from .forms import OrderForm, FabricPurchasedForm, PrintingAndDyeingForm, ClothCuttingForm, StitchingForm, FinishingAndPackingForm, DispatchForm

# Create your views here.
@login_required
def index(request):
    orders = Order.objects.all().order_by('-id')
    return render(request, 'index.html', {'orders': orders})

    # This is index function with additional data fetching and processing
    # orders = Order.objects.all().order_by('-order_date')
    
    # # Get monthly revenue data
    # monthly_revenue = Order.objects.annotate(
    #     month=TruncMonth('order_date')
    # ).values('month').annotate(
    #     total=Sum('amount')
    # ).order_by('month')
    
    # # Get top customers by order volume
    # top_customers = Order.objects.values('order_received_from').annotate(
    #     total_quantity=Sum('quantity'),
    #     order_count=Count('id')
    # ).order_by('-total_quantity')[:5]
    
    # context = {
    #     'orders': orders,
    #     'STATUS': Order.STATUS,
    #     'monthly_revenue': monthly_revenue,
    #     'top_customers': top_customers,
    # }
    # return render(request, 'index2.html', context)

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
    printing_dyeing = PrintingAndDyeing.objects.filter(order=order).first()
    cloth_cutting = ClothCutting.objects.filter(order=order).first()
    stitching = Stitching.objects.filter(order=order).first()
    finishing_packing = FinishingAndPacking.objects.filter(order=order).first()
    dispatch = Dispatch.objects.filter(order=order).first()
    
    context = {
        'order': order,
        'fabric_purchased': fabric_purchased,
        'printing_dyeing': printing_dyeing,
        'cloth_cutting': cloth_cutting, 
        'stitching': stitching,
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
def add_printinganddyeing(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'Fabric Purchased':
        messages.error(request, 'Printing and dyeing details can only be added to orders with status "Fabric Purchased".')
        return redirect('orderdetail', id=id)
                        
    if request.method == 'POST':
        form = PrintingAndDyeingForm(request.POST)
        if form.is_valid():
            printing_dyeing = form.save(commit=False)
            printing_dyeing.order = order
            printing_dyeing.user = request.user
            printing_dyeing.save()
            messages.success(request, 'Printing and dyeing details added successfully.')
            return redirect('orderdetail', id=id)
    else:
        form = PrintingAndDyeingForm()
    return render(request, 'add_printinganddyeing.html', {'form': form, 'order': order})

@login_required
def add_clothcutting(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'Printing and Dyeing':
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
def add_finishingandpacking(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'Stitching':
        messages.error(request, 'Finishing and packing details can only be added to orders with status "Stitching".')
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