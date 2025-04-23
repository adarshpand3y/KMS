# yourapp/management/commands/export_orders.py

import csv
import os
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import models
from mainapp.models import (
    Order, FabricPurchased, PrintingAndDyeing, ClothCutting, 
    Stitching, ExtraWork, FinishingAndPacking, Dispatch
)

class Command(BaseCommand):
    help = 'Export all orders with their associated data to a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default=f'orders_export_{str(datetime.datetime.now().timestamp()).replace(" ", "_")}.csv',
                            help='Filename for the CSV export')
        parser.add_argument('--path', type=str, default=None,
                            help='Path to save the CSV file (defaults to MEDIA_ROOT/exports)')
        parser.add_argument('--batch-size', type=int, default=1000,
                            help='Number of records to process in each batch')

    def handle(self, *args, **options):
        # Determine the file path
        filename = options['output']
        if options['path']:
            export_path = options['path']
        else:
            export_path = os.path.join(settings.MEDIA_ROOT, 'exports')
        
        # Create directory if it doesn't exist
        os.makedirs(export_path, exist_ok=True)
        
        file_path = os.path.join(export_path, filename)
        batch_size = options['batch_size']
        
        # Create field names for the CSV
        field_names = self._get_field_names()
        
        # Count total orders for progress reporting
        total_orders = Order.objects.count()
        self.stdout.write(f'Starting export of {total_orders} orders')
        
        # Write to CSV file using batches
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            
            # Write header row
            writer.writeheader()
            
            # Process in batches
            processed = 0
            
            # Get the maximum order ID to use for batching
            if total_orders > 0:
                max_id = Order.objects.aggregate(models.Max('id'))['id__max']
                
                # Process in batches based on ID ranges
                for start_id in range(0, max_id + 1, batch_size):
                    end_id = min(start_id + batch_size - 1, max_id)
                    
                    # Query this batch of orders
                    batch = Order.objects.filter(id__gte=start_id, id__lte=end_id)
                    
                    # Get all related data for this batch in a single query per model
                    order_ids = list(batch.values_list('id', flat=True))
                    
                    # Query all related models for this batch
                    fabrics = {item.order_id: item for item in 
                              FabricPurchased.objects.filter(order_id__in=order_ids)}
                    
                    printings = {item.order_id: item for item in 
                                PrintingAndDyeing.objects.filter(order_id__in=order_ids)}
                    
                    cuttings = {item.order_id: item for item in 
                               ClothCutting.objects.filter(order_id__in=order_ids)}
                    
                    stitchings = {item.order_id: item for item in 
                                 Stitching.objects.filter(order_id__in=order_ids)}
                    
                    extras = {item.order_id: item for item in 
                             ExtraWork.objects.filter(order_id__in=order_ids)}
                    
                    finishings = {item.order_id: item for item in 
                                 FinishingAndPacking.objects.filter(order_id__in=order_ids)}
                    
                    dispatches = {item.order_id: item for item in 
                                 Dispatch.objects.filter(order_id__in=order_ids)}
                    
                    # Process each order in the batch
                    for order in batch:
                        # Get all data with efficient lookups
                        row = self._get_order_data(
                            order, 
                            fabrics.get(order.id),
                            printings.get(order.id),
                            cuttings.get(order.id),
                            stitchings.get(order.id),
                            extras.get(order.id),
                            finishings.get(order.id),
                            dispatches.get(order.id)
                        )
                        writer.writerow(row)
                        processed += 1
                    
                    # Report progress
                    self.stdout.write(f'Processed {processed}/{total_orders} orders')
            
        self.stdout.write(self.style.SUCCESS(f'Successfully exported {processed} orders to {file_path}'))
        return file_path
    
    def _get_field_names(self):
        """Generate all field names for the CSV header"""
        # Same as before - field definitions
        # Order fields
        fields = [
            'order_id', 'order_date', 'style_id', 'order_received_from', 
            'quantity', 'size', 'rate', 'status', 'amount'
        ]
        
        # FabricPurchased fields
        fields.extend([
            'fabric_purchase_date', 'purchased_from', 'fabric_quantity', 
            'fabric_rate', 'fabric_amount', 'invoice_number', 'fabric_detail',
            'fabric_length', 'fabric_dyer', 'challan_number', 'issued_challan_date',
            'fabric_issued_challan_quantity', 'balance_fabric'
        ])
        
        # Add all other fields like before...
        # (including all fields from PrintingAndDyeing, ClothCutting, etc.)
        # Fields for other models would go here, same as original implementation
        
        # PrintingAndDyeing fields
        fields.extend([
            'print_issued_challan_date', 'print_issued_challan_number', 
            'dyer_printer_name', 'print_fabric_detail', 'print_fabric_length',
            'print_issued_challan_quantity', 'shrinkage_in_percentage',
            'print_received_quantity', 'print_balance_quantity', 
            'print_received_date', 'print_received_challan_number',
            'print_rate', 'print_amount'
        ])
        
        # ClothCutting fields
        fields.extend([
            'cut_issued_challan_date', 'cut_issued_challan_number',
            'cut_job_worker_name', 'cut_fabric_detail', 'cut_fabric_length',
            'cut_issued_challan_quantity', 'cut_received_quantity',
            'cut_balance_quantity', 'cut_received_date', 
            'cut_received_challan_number', 'cut_rate', 'cut_amount'
        ])
        
        # Stitching fields
        fields.extend([
            'stitch_issued_challan_date', 'stitch_issued_challan_number',
            'stitch_job_worker_name', 'stitch_issued_challan_quantity',
            'stitch_received_quantity', 'stitch_balance_quantity',
            'stitch_received_date', 'stitch_rate', 'stitch_amount'
        ])
        
        # ExtraWork fields
        fields.extend([
            'extra_issued_challan_date', 'extra_issued_challan_number',
            'extra_job_worker_name', 'extra_work_name', 
            'extra_issued_challan_quantity', 'extra_received_quantity',
            'extra_balance_quantity', 'extra_rate', 'extra_amount',
            'extra_received_date'
        ])
        
        # FinishingAndPacking fields
        fields.extend([
            'finish_issued_challan_date', 'finish_issued_challan_number',
            'finish_job_worker_name', 'finish_issued_challan_quantity',
            'packed_quantity', 'rejected', 'finish_rate', 'finish_amount'
        ])
        
        # Dispatch fields
        fields.extend([
            'dispatch_date', 'dispatched_to', 'dispatch_quantity',
            'delivery_note', 'dispatch_invoice_number'
        ])
        
        return fields
    
    def _get_order_data(self, order, fabric=None, printing=None, cutting=None, 
                        stitching=None, extra=None, finishing=None, dispatch=None):
        """Get all data for an order and its related models"""
        # Start with order data
        data = {
            'order_id': order.id,
            'order_date': order.order_date,
            'style_id': order.style_id,
            'order_received_from': order.order_received_from,
            'quantity': order.quantity,
            'size': order.size,
            'rate': order.rate,
            'status': order.status,
            'amount': order.amount
        }
        
        # Initialize all fields with empty values first
        # This is more efficient than setting each field separately in the else clauses
        for field in self._get_field_names()[8:]:  # Skip the order fields we already set
            data[field] = ""
        
        # Update with related model data if available
        if fabric:
            data.update({
                'fabric_purchase_date': fabric.fabric_purchase_date,
                'purchased_from': fabric.purchased_from,
                'fabric_quantity': fabric.quantity,
                'fabric_rate': fabric.rate,
                'fabric_amount': fabric.amount,
                'invoice_number': fabric.invoice_number,
                'fabric_detail': fabric.fabric_detail,
                'fabric_length': fabric.fabric_length,
                'fabric_dyer': fabric.fabric_dyer,
                'challan_number': fabric.challan_number,
                'issued_challan_date': fabric.issued_challan_date,
                'fabric_issued_challan_quantity': fabric.issued_challan_quantity,
                'balance_fabric': fabric.balance_fabric
            })
        
        if printing:
            data.update({
                'print_issued_challan_date': printing.issued_challan_date,
                # 'print_issued_challan_number': printing.issued_challan_number,
                'dyer_printer_name': printing.dyer_printer_name,
                'print_fabric_detail': printing.fabric_detail,
                'print_fabric_length': printing.fabric_length,
                'print_issued_challan_quantity': printing.issued_challan_quantity,
                'shrinkage_in_percentage': printing.shrinkage_in_percentage,
                'print_received_quantity': printing.received_quantity,
                'print_balance_quantity': printing.balance_quantity,
                'print_received_date': printing.received_date,
                'print_received_challan_number': printing.received_challan_number,
                'print_rate': printing.rate,
                'print_amount': printing.amount
            })
        
        # Add all other model data the same way
        # This follows the same pattern for all remaining models
        
        if cutting:
            data.update({
                'cut_issued_challan_date': cutting.issued_challan_date,
                'cut_issued_challan_number': cutting.issued_challan_number,
                'cut_job_worker_name': cutting.job_worker_name,
                'cut_fabric_detail': cutting.fabric_detail,
                'cut_fabric_length': cutting.fabric_length,
                'cut_issued_challan_quantity': cutting.issued_challan_quantity,
                'cut_received_quantity': cutting.received_quantity,
                'cut_balance_quantity': cutting.balance_quantity,
                'cut_received_date': cutting.received_date,
                'cut_received_challan_number': cutting.received_challan_number,
                'cut_rate': cutting.rate,
                'cut_amount': cutting.amount
            })
        
        if stitching:
            data.update({
                'stitch_issued_challan_date': stitching.issued_challan_date,
                'stitch_issued_challan_number': stitching.issued_challan_number,
                'stitch_job_worker_name': stitching.job_worker_name,
                'stitch_issued_challan_quantity': stitching.issued_challan_quantity,
                'stitch_received_quantity': stitching.received_quantity,
                'stitch_balance_quantity': stitching.balance_quantity,
                'stitch_received_date': stitching.received_date,
                'stitch_rate': stitching.rate,
                'stitch_amount': stitching.amount
            })
        
        if extra:
            data.update({
                'extra_issued_challan_date': extra.issued_challan_date,
                'extra_issued_challan_number': extra.issued_challan_number,
                'extra_job_worker_name': extra.job_worker_name,
                'extra_work_name': extra.extra_work_name,
                'extra_issued_challan_quantity': extra.issued_challan_quantity,
                'extra_received_quantity': extra.received_quantity,
                'extra_balance_quantity': extra.balance_quantity,
                'extra_rate': extra.rate,
                'extra_amount': extra.amount,
                'extra_received_date': extra.received_date
            })
        
        if finishing:
            data.update({
                'finish_issued_challan_date': finishing.issued_challan_date,
                'finish_issued_challan_number': finishing.issued_challan_number,
                'finish_job_worker_name': finishing.job_worker_name,
                'finish_issued_challan_quantity': finishing.issued_challan_quantity,
                'packed_quantity': finishing.packed_quantity,
                'rejected': finishing.rejected,
                'finish_rate': finishing.rate,
                'finish_amount': finishing.amount
            })
        
        if dispatch:
            data.update({
                'dispatch_date': dispatch.dispatch_date,
                'dispatched_to': dispatch.dispatched_to,
                'dispatch_quantity': dispatch.quantity,
                'delivery_note': dispatch.delivery_note,
                'dispatch_invoice_number': dispatch.invoice_number
            })
        
        return data