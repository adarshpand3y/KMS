from django.contrib import admin
from .models import Order, FabricPurchased, PrintingAndDyeing, ClothCutting, Stitching, FinishingAndPacking, Dispatch









from django.contrib import admin
from .models import (
    Order, 
    FabricPurchased, 
    PrintingAndDyeing, 
    ClothCutting, 
    Stitching, 
    FinishingAndPacking, 
    Dispatch
)

class OrderAdmin(admin.ModelAdmin):
    # Configure display, filter, search options as needed
    list_display = ['style_id', 'order_received_from', 'quantity', 'rate', 'amount', 'status', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['style_id', 'order_received_from']
    
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

class FabricPurchasedAdmin(admin.ModelAdmin):
    list_display = ['order', 'purchased_from', 'quantity', 'rate', 'amount', 'fabric_purchase_date']
    list_filter = ['fabric_purchase_date']
    search_fields = ['order__style_id', 'purchased_from', 'invoice_number']
    
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

class PrintingAndDyeingAdmin(admin.ModelAdmin):
    list_display = ['order', 'dyer_printer_name', 'issued_challan_quantity', 'received_quantity', 'balance_quantity']
    list_filter = ['issued_challan_date', 'received_date']
    search_fields = ['order__style_id', 'dyer_printer_name', 'issued_challan_number']
    
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

class ClothCuttingAdmin(admin.ModelAdmin):
    list_display = ['order', 'job_worker_name', 'issued_challan_quantity', 'received_quantity', 'balance_quantity']
    list_filter = ['issued_challan_date', 'received_date']
    search_fields = ['order__style_id', 'job_worker_name', 'issued_challan_number']
    
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

class StitchingAdmin(admin.ModelAdmin):
    list_display = ['order', 'job_worker_name', 'issued_challan_quantity', 'received_quantity', 'balance_quantity']
    list_filter = ['issued_challan_date', 'received_date']
    search_fields = ['order__style_id', 'job_worker_name', 'issued_challan_number']
    
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

class FinishingAndPackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'job_worker_name', 'issued_challan_quantity', 'packed_quantity', 'rejected']
    list_filter = ['issued_challan_date']
    search_fields = ['order__style_id', 'job_worker_name', 'issued_challan_number']
    
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

class DispatchAdmin(admin.ModelAdmin):
    list_display = ['order', 'dispatched_to', 'quantity', 'invoice_number', 'dispatch_date']
    list_filter = ['dispatch_date']
    search_fields = ['order__style_id', 'dispatched_to', 'invoice_number']
    
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

# Register your models here.
admin.site.register(Order, OrderAdmin)
admin.site.register(FabricPurchased, FabricPurchasedAdmin)
admin.site.register(PrintingAndDyeing, PrintingAndDyeingAdmin)
admin.site.register(ClothCutting, ClothCuttingAdmin)
admin.site.register(Stitching, StitchingAdmin)
admin.site.register(FinishingAndPacking, FinishingAndPackingAdmin)
admin.site.register(Dispatch, DispatchAdmin)
