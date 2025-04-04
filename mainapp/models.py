from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import datetime

# Create your models here.
class Order(models.Model):
    STATUS = [
        ('Pending', 'Pending'),
        ('Fabric Purchased', 'Fabric Purchased'),
        ('Printing and Dyeing', 'Printing and Dyeing'),
        ('Cloth Cutting', 'Cloth Cutting'),
        ('Stitching', 'Stitching'),
        ('Extra Work', 'Extra Work'),
        ('Finishing and Packing', 'Finishing and Packing'),
        ('Dispatched', 'Dispatched'),
    ]

    order_date = models.DateField(default=datetime.date.today)
    style_id = models.CharField(max_length=20)
    order_received_from = models.CharField(max_length=20)
    quantity = models.IntegerField()
    rate = models.IntegerField()    
    
    status = models.CharField(
        max_length=50,
        choices=STATUS,
        default='Pending',
    )
    amount = models.BigIntegerField(blank=True) # calculated field

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Order # {self.style_id} - {self.order_received_from}"

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)

class FabricPurchased(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    fabric_purchase_date = models.DateField(default=datetime.date.today)
    # style_id - will get from linked parent order
    purchased_from = models.CharField(max_length=100)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True) # calculated field
    invoice_number = models.CharField(max_length=50)
    fabric_detail = models.CharField(max_length=100)
    fabric_length = models.CharField(max_length=20)
    fabric_dyer = models.CharField(max_length=100)
    challan_number = models.CharField(max_length=50)
    issued_challan_date = models.DateField(default=datetime.date.today)
    issued_challan_quantity = models.IntegerField()
    balance_fabric = models.DecimalField(max_digits=10, decimal_places=2, blank=True) # calculated field

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Fabric Purchased for Order # {self.order.style_id}"

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate
        self.balance_fabric = self.issued_challan_quantity - self.quantity
        if self.order.status == 'Pending':
            self.order.status = 'Fabric Purchased'
            self.order.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Fabric Purchased"
    
    # def clean(self):
    #     cleaned_data = super().clean()

    #     # This is just demonstration of how to raise a validation error
    #     raise ValidationError(["This is a custom validation error.", "qer"])

    #     return cleaned_data

class PrintingAndDyeing(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    issued_challan_date = models.DateField(default=datetime.date.today)
    issued_challan_number = models.CharField(max_length=50)
    # sending details
    # style_id - will get from linked parent order
    dyer_printer_name = models.CharField(max_length=100)
    fabric_detail = models.CharField(max_length=100)
    fabric_length = models.CharField(max_length=20)
    issued_challan_quantity = models.IntegerField()
    # receiving details
    shrinkage_in_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    received_quantity = models.IntegerField()
    balance_quantity = models.IntegerField(blank=True) # calculated field
    received_date = models.DateField(default=datetime.date.today)
    received_challan_number = models.CharField(max_length=50)
    # dyer invoice details
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True) # calculated field

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Printing & Dyeing for Order # {self.order.style_id}"

    def save(self, *args, **kwargs):
        self.received_quantity = self.issued_challan_quantity - (self.issued_challan_quantity * self.shrinkage_in_percentage / 100)
        self.balance_quantity = self.issued_challan_quantity - self.received_quantity
        self.amount = self.received_quantity * self.rate
        if self.order.status == 'Fabric Purchased':
            self.order.status = 'Printing and Dyeing'
            self.order.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Printing and Dyeing"

class ClothCutting(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    issued_challan_date = models.DateField(default=datetime.date.today)
    issued_challan_number = models.CharField(max_length=50)
    # sending details
    # style_id - will get from linked parent order
    job_worker_name = models.CharField(max_length=100)
    fabric_detail = models.CharField(max_length=100)
    fabric_length = models.CharField(max_length=20)
    issued_challan_quantity = models.IntegerField()
    # receiving details
    received_quantity = models.IntegerField()
    balance_quantity = models.IntegerField(blank=True) # calculated field
    received_date = models.DateField(default=datetime.date.today)
    received_challan_number = models.CharField(max_length=50)
    # job worker invoice
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True) # calculated field

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Cloth Cutting for Order # {self.order.style_id}"

    def save(self, *args, **kwargs):
        self.balance_quantity = self.issued_challan_quantity - self.received_quantity
        self.amount = self.received_quantity * self.rate
        if self.order.status == 'Printing and Dyeing':
            self.order.status = 'Cloth Cutting'
            self.order.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Cloth Cutting"

class Stitching(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    issued_challan_date = models.DateField(default=datetime.date.today)
    issued_challan_number = models.CharField(max_length=50)
    # sending details
    # style_id - will get from linked parent order
    job_worker_name = models.CharField(max_length=100)
    issued_challan_quantity = models.IntegerField()
    # receiving details
    received_quantity = models.IntegerField()
    balance_quantity = models.IntegerField(blank=True) # calculated field
    received_date = models.DateField(default=datetime.date.today)
    # job_worker_invoice
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True) # calculated field

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Stitching for Order # {self.order.style_id}"

    def save(self, *args, **kwargs):
        self.balance_quantity = self.issued_challan_quantity - self.received_quantity
        self.amount = self.received_quantity * self.rate
        if self.order.status == 'Cloth Cutting':
            self.order.status = 'Stitching'
            self.order.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Stitching"

class ExtraWork(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    issued_challan_date = models.DateField(default=datetime.date.today)
    issued_challan_number = models.CharField(max_length=50)
    # style_id - will get from linked parent order
    # sending details
    job_worker_name = models.CharField(max_length=100)
    extra_work_name = models.CharField(max_length=100)
    issued_challan_quantity = models.IntegerField()
    # receiving details
    received_quantity = models.IntegerField()
    balance_quantity = models.IntegerField(blank=True) # calculated field
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True) # calculated field
    received_date = models.DateField(default=datetime.date.today)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Extra Work for Order # {self.order.style_id}"
    
    def save(self, *args, **kwargs):
        self.balance_quantity = self.issued_challan_quantity - self.received_quantity
        self.amount = self.received_quantity * self.rate
        if self.order.status == 'Stitching':
            self.order.status = 'Extra Work'
            self.order.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Extra Work"

class FinishingAndPacking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    issued_challan_date = models.DateField(default=datetime.date.today)
    issued_challan_number = models.CharField(max_length=50)
    # sending details
    # style_id - will get from linked parent order
    job_worker_name = models.CharField(max_length=100)
    issued_challan_quantity = models.IntegerField()
    packed_quantity = models.IntegerField()
    rejected = models.IntegerField(blank=True) # calculated field
    # job worker invoice detail
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True) # calculated field

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Finishing & Packing for Order # {self.order.style_id}"

    def save(self, *args, **kwargs):
        self.rejected = self.issued_challan_quantity - self.packed_quantity
        self.amount = self.packed_quantity * self.rate
        if self.order.status == 'Extra Work':
            self.order.status = 'Finishing and Packing'
            self.order.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Finishing and Packing"

class Dispatch(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dispatch_date = models.DateField(default=datetime.date.today)
    # style_id - will get from linked parent order
    dispatched_to = models.CharField(max_length=100)
    quantity = models.IntegerField()
    delivery_note = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=50)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Dispatch for Order # {self.order.style_id}"

    def save(self, *args, **kwargs):
        if self.order.status == 'Finishing and Packing':
            self.order.status = 'Dispatched'
            self.order.save()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Dispatch"