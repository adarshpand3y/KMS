from django import forms
from .models import Order, FabricPurchased, PrintingAndDyeing, ClothCutting, Stitching, ExtraWork, FinishingAndPacking, Dispatch

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['style_id', 'order_received_from', 'quantity', 'rate']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class FabricPurchasedForm(forms.ModelForm):
    class Meta:
        model = FabricPurchased
        fields = ['fabric_purchase_date', 'purchased_from', 'quantity', 'rate', 'invoice_number', 
                  'fabric_detail', 'fabric_length', 'fabric_dyer', 'challan_number', 'issued_challan_date', 
                  'issued_challan_quantity']
        widgets = {
            'fabric_purchase_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'issued_challan_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class PrintingAndDyeingForm(forms.ModelForm):
    class Meta:
        model = PrintingAndDyeing
        fields = ['issued_challan_date', 'dyer_printer_name', 'fabric_detail', 
                  'fabric_length', 'issued_challan_quantity', 'shrinkage_in_percentage', 'received_quantity', 
                  'received_date', 'received_challan_number', 'rate']
        widgets = {
            'issued_challan_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'received_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class ClothCuttingForm(forms.ModelForm):
    class Meta:
        model = ClothCutting
        fields = ['issued_challan_date', 'issued_challan_number', 'job_worker_name', 'fabric_detail', 
                  'fabric_length', 'issued_challan_quantity', 'received_quantity', 'received_date',
                  'received_challan_number', 'rate']
        widgets = {
            'issued_challan_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'received_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class StitchingForm(forms.ModelForm):
    class Meta:
        model = Stitching
        fields = ['issued_challan_date', 'issued_challan_number', 'job_worker_name', 
                  'issued_challan_quantity', 'received_quantity', 'rate']
        widgets = {
            'issued_challan_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class ExtraWorkForm(forms.ModelForm):
    class Meta:
        model = ExtraWork
        fields = ['issued_challan_date', 'issued_challan_number', 'job_worker_name', 'extra_work_name', 
                  'issued_challan_quantity', 'received_quantity', 'rate']
        widgets = {
            'issued_challan_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class FinishingAndPackingForm(forms.ModelForm):
    class Meta:
        model = FinishingAndPacking
        fields = ['issued_challan_date', 'issued_challan_number', 'job_worker_name', 'issued_challan_quantity', 
                  'packed_quantity', 'rate']
        widgets = {
            'issued_challan_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class DispatchForm(forms.ModelForm):
    class Meta:
        model = Dispatch
        fields = ['dispatch_date', 'dispatched_to', 'quantity', 'delivery_note', 'invoice_number']
        widgets = {
            'dispatch_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

