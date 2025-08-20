from django import forms
from django.utils.safestring import mark_safe
from .models import Order, FabricPurchased, PrintingAndDyeingSent, PrintingAndDyeingReceived, ClothCutting, Stitching, ExtraWork, FinishingAndPacking, Dispatch
from crispy_forms.helper import FormHelper

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['po_number', 'style_id', 'order_received_from', 
                  'quantity_xs', 'quantity_s', 'quantity_m', 'quantity_l', 'quantity_xl', 
                  'quantity_2xl', 'quantity_3xl', 'quantity_4xl', 'quantity_5xl',
                  'quantity_6xl', 'quantity_7xl', 'quantity_8xl', 'quantity_9xl', 'quantity_10xl',
                  'rate', 'order_date']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class FabricPurchasedForm(forms.ModelForm):
    class Meta:
        model = FabricPurchased
        fields = ['fabric_purchase_date', 'purchased_from', 'quantity', 'rate', 'invoice_number', 
                  'fabric_detail', 'fabric_length', 'fabric_dyer']
        widgets = {
            'fabric_purchase_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'issued_challan_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class PrintingAndDyeingSentForm(forms.ModelForm):
    class Meta:
        model = PrintingAndDyeingSent
        fields = ['issued_challan_date', 'dyer_printer_name', 'fabric_detail', 
                  'fabric_length', 'issued_challan_quantity']
        widgets = {
            'issued_challan_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }

class PrintingAndDyeingReceivedForm(forms.ModelForm):
    class Meta:
        model = PrintingAndDyeingReceived
        fields = ['shrinkage_in_percentage', 'received_date', 
                  'received_challan_number', 'rate']
        widgets = {
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
        fields = ['dispatch_date', 'dispatched_to', 'quantity', 'delivery_note', 'invoice_number', 'box_details']
        widgets = {
            'dispatch_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional: Add help_text if not set in model
        self.fields['box_details'].help_text = mark_safe(
            '<ul class="form-text text-muted">'
            '<li>Enter the box contents here.</li>'
            '<li>Each line represents the box number.</li>'
            '<li>In each line, enter the size contents and its quantity.</li>'
            '<li>Example line 1: XS - 10, M, 20</li>'
            '<li>Example line 2: XS - 25, L, 50</li>'
            '</ul>'
        )

        # Crispy helper without layout
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.label_class = 'form-label'
        self.helper.field_class = 'form-control'
