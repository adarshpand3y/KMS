from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
import random
from datetime import timedelta, datetime
import calendar

from mainapp.models import (
    Order, 
    FabricPurchased, 
    PrintingAndDyeing, 
    ClothCutting,
    Stitching,
    ExtraWork,
    FinishingAndPacking,
    Dispatch
)

class Command(BaseCommand):
    help = 'Generates fake data for clothing production management system'

    def add_arguments(self, parser):
        parser.add_argument('--orders', type=int, default=100, help='Number of orders to generate')
        parser.add_argument('--user', type=str, default=None, help='Username to associate with records')
        parser.add_argument('--complete', action='store_true', help='Generate complete lifecycle for some orders')

    def handle(self, *args, **options):
        fake = Faker()
        num_orders = options['orders']
        user = None
        
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
                self.stdout.write(self.style.SUCCESS(f'Using user: {user.username}'))
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User {options["user"]} not found. Creating records without user.'))
        
        # Get current month's date range
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        last_day = datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        
        # Create orders within the current month
        self.stdout.write(f'Generating {num_orders} orders for the current month ({today.strftime("%B %Y")})...')
        orders = []
        for _ in range(num_orders):
            # Create a random date within the current month
            # order_date = fake.date_between(start_date=first_day, end_date=last_day) # Random date within the month
            order_date = fake.date_between(start_date=first_day, end_date=min(last_day, today)) # Random date within the month or today
            
            order = Order(
                order_date=order_date,  # Explicitly set order date
                style_id=f'STY-{fake.bothify(text="??###")}',
                order_received_from=fake.company(),
                quantity=random.randint(100, 500),
                rate=random.randint(200, 2000),
                user=user
            )
            order.save()
            orders.append(order)
            self.stdout.write(f'Created order: {order} on {order.order_date}')
            
        # Generate complete lifecycle for some orders if requested
        if options['complete']:
            complete_orders = random.sample(orders, min(len(orders), max(1, num_orders // 2)))
            for order in complete_orders:
                self._generate_full_lifecycle(order, fake, user, last_day)
        else:
            # Otherwise, generate random stages
            for order in orders:
                # Randomly decide how far in the process this order should go
                stage = random.randint(0, 7)  # 0-7 for the 8 possible statuses
                if stage >= 1:
                    self._create_fabric_purchased(order, fake, user, last_day=last_day)
                if stage >= 2:
                    self._create_printing_and_dyeing(order, fake, user, last_day=last_day)
                if stage >= 3:
                    self._create_cloth_cutting(order, fake, user, last_day=last_day)
                if stage >= 4:
                    self._create_stitching(order, fake, user, last_day=last_day)
                if stage >= 5:
                    self._create_extra_work(order, fake, user, last_day=last_day)
                if stage >= 6:
                    self._create_finishing_and_packing(order, fake, user, last_day=last_day)
                if stage >= 7:
                    self._create_dispatch(order, fake, user, last_day=last_day)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated data for {num_orders} orders within {today.strftime("%B %Y")}'))

    def _generate_full_lifecycle(self, order, fake, user, last_day=None):
        """Generate a complete lifecycle for an order with realistic dates"""
        self.stdout.write(f'Generating complete lifecycle for order {order}')
        
        # Start date is the order date
        current_date = order.order_date
        remaining_days = (last_day.date() - current_date).days if last_day else 30
        
        # If very few days remain, compress the timeline
        time_compression = max(1, remaining_days / 30)  # Scale factor for timeline compression
        
        # Add 1-3 days for fabric purchase (scaled)
        days_to_add = max(1, int(random.randint(1, 3) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        fabric = self._create_fabric_purchased(order, fake, user, current_date)
        
        # Add 3-7 days for printing and dyeing (scaled)
        days_to_add = max(1, int(random.randint(3, 7) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        pd = self._create_printing_and_dyeing(order, fake, user, current_date)
        
        # Add 2-4 days for cloth cutting (scaled)
        days_to_add = max(1, int(random.randint(2, 4) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        cutting = self._create_cloth_cutting(order, fake, user, current_date)
        
        # Add 4-10 days for stitching (scaled)
        days_to_add = max(1, int(random.randint(4, 10) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        stitching = self._create_stitching(order, fake, user, current_date)
        
        # Add 2-5 days for extra work (scaled)
        days_to_add = max(1, int(random.randint(2, 5) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        extra = self._create_extra_work(order, fake, user, current_date)
        
        # Add 1-3 days for finishing and packing (scaled)
        days_to_add = max(1, int(random.randint(1, 3) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        finishing = self._create_finishing_and_packing(order, fake, user, current_date)
        
        # Add 1-2 days for dispatch (scaled)
        days_to_add = max(1, int(random.randint(1, 2) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        dispatch = self._create_dispatch(order, fake, user, current_date)
        
        self.stdout.write(self.style.SUCCESS(f'Completed full lifecycle for order {order}'))
        
    def _create_fabric_purchased(self, order, fake, user, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=30)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Ensure challan date doesn't exceed month end
        challan_days = random.randint(1, 3)
        challan_date = date + timedelta(days=challan_days)
        if last_day and challan_date > last_day.date():
            challan_date = last_day.date()
        
        quantity = order.quantity * random.uniform(1.1, 1.3)  # Need more fabric than final quantity
        challan_quantity = quantity * random.uniform(0.9, 1.0)  # Some fabric might be held back
        
        fabric = FabricPurchased(
            order=order,
            fabric_purchase_date=date,
            purchased_from=fake.company(),
            quantity=int(quantity),
            rate=random.uniform(50, 200),
            invoice_number=f'INV-{fake.bothify(text="######")}',
            fabric_detail=random.choice(['Cotton', 'Linen', 'Silk', 'Wool', 'Polyester', 'Rayon']),
            fabric_length=f'{random.randint(40, 60)}"{random.choice(["", "/", "x"])}{random.randint(40, 60)}"',
            fabric_dyer=fake.company(),
            challan_number=f'CHN-{fake.bothify(text="######")}',
            issued_challan_date=challan_date,
            issued_challan_quantity=int(challan_quantity),
            user=user
        )
        fabric.save()
        return fabric

    def _create_printing_and_dyeing(self, order, fake, user, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=45)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Ensure receive date doesn't exceed month end
        receive_days = random.randint(2, 5)
        receive_date = date + timedelta(days=receive_days)
        if last_day and receive_date > last_day.date():
            receive_date = last_day.date()
        
        # Get quantities from previous step if available
        try:
            fabric = FabricPurchased.objects.filter(order=order).latest('fabric_purchase_date')
            challan_quantity = fabric.issued_challan_quantity
        except FabricPurchased.DoesNotExist:
            challan_quantity = order.quantity * random.uniform(1.1, 1.3)
        
        shrinkage = random.uniform(1, 10)
        received_qty = int(challan_quantity * (1 - shrinkage/100))
        
        pd = PrintingAndDyeing(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'PDC-{fake.bothify(text="######")}',
            dyer_printer_name=fake.company(),
            fabric_detail=random.choice(['Cotton', 'Linen', 'Silk', 'Wool', 'Polyester', 'Rayon']),
            fabric_length=f'{random.randint(40, 60)}"{random.choice(["", "/", "x"])}{random.randint(40, 60)}"',
            issued_challan_quantity=int(challan_quantity),
            shrinkage_in_percentage=shrinkage,
            received_quantity=received_qty,
            received_date=receive_date,
            received_challan_number=f'RCV-{fake.bothify(text="######")}',
            rate=random.uniform(30, 100),
            user=user
        )
        pd.save()
        return pd

    def _create_cloth_cutting(self, order, fake, user, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=60)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Ensure receive date doesn't exceed month end
        receive_days = random.randint(1, 3)
        receive_date = date + timedelta(days=receive_days)
        if last_day and receive_date > last_day.date():
            receive_date = last_day.date()
        
        # Get quantities from previous step if available
        try:
            pd = PrintingAndDyeing.objects.filter(order=order).latest('issued_challan_date')
            challan_quantity = pd.received_quantity
        except PrintingAndDyeing.DoesNotExist:
            challan_quantity = order.quantity * random.uniform(1.0, 1.1)
        
        # Some material may be lost in cutting
        received_qty = int(challan_quantity * random.uniform(0.9, 0.98))
        
        cutting = ClothCutting(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'CUT-{fake.bothify(text="######")}',
            job_worker_name=fake.company(),
            fabric_detail=random.choice(['Cotton', 'Linen', 'Silk', 'Wool', 'Polyester', 'Rayon']),
            fabric_length=f'{random.randint(40, 60)}"{random.choice(["", "/", "x"])}{random.randint(40, 60)}"',
            issued_challan_quantity=int(challan_quantity),
            received_quantity=received_qty,
            received_date=receive_date,
            received_challan_number=f'RCV-{fake.bothify(text="######")}',
            rate=random.uniform(10, 50),
            user=user
        )
        cutting.save()
        return cutting

    def _create_stitching(self, order, fake, user, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=75)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Ensure receive date doesn't exceed month end
        receive_days = random.randint(3, 7)
        receive_date = date + timedelta(days=receive_days)
        if last_day and receive_date > last_day.date():
            receive_date = last_day.date()
        
        # Get quantities from previous step if available
        try:
            cutting = ClothCutting.objects.filter(order=order).latest('issued_challan_date')
            challan_quantity = cutting.received_quantity
        except ClothCutting.DoesNotExist:
            challan_quantity = order.quantity * random.uniform(0.95, 1.05)
        
        # Some pieces may be rejected during stitching
        received_qty = int(challan_quantity * random.uniform(0.92, 0.98))
        
        stitching = Stitching(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'STI-{fake.bothify(text="######")}',
            job_worker_name=fake.company(),
            issued_challan_quantity=int(challan_quantity),
            received_quantity=received_qty,
            received_date=receive_date,
            rate=random.uniform(50, 200),
            user=user
        )
        stitching.save()
        return stitching

    def _create_extra_work(self, order, fake, user, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=90)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Ensure receive date doesn't exceed month end
        receive_days = random.randint(2, 5)
        receive_date = date + timedelta(days=receive_days)
        if last_day and receive_date > last_day.date():
            receive_date = last_day.date()
        
        # Get quantities from previous step if available
        try:
            stitching = Stitching.objects.filter(order=order).latest('issued_challan_date')
            challan_quantity = stitching.received_quantity
        except Stitching.DoesNotExist:
            challan_quantity = order.quantity * random.uniform(0.9, 1.0)
        
        # Most pieces should pass extra work
        received_qty = int(challan_quantity * random.uniform(0.95, 0.99))
        
        extra_work = ExtraWork(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'EXT-{fake.bothify(text="######")}',
            job_worker_name=fake.company(),
            extra_work_name=random.choice(['Embroidery', 'Beading', 'Sequins', 'Appliqué', 'Pleating', 'Printing']),
            issued_challan_quantity=int(challan_quantity),
            received_quantity=received_qty,
            received_date=receive_date,
            rate=random.uniform(20, 100),
            user=user
        )
        extra_work.save()
        return extra_work

    def _create_finishing_and_packing(self, order, fake, user, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=100)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
        
        # Get quantities from previous step if available
        try:
            extra_work = ExtraWork.objects.filter(order=order).latest('issued_challan_date')
            challan_quantity = extra_work.received_quantity
        except ExtraWork.DoesNotExist:
            challan_quantity = order.quantity * random.uniform(0.85, 0.95)
        
        # Some pieces may be rejected during final inspection
        packed_qty = int(challan_quantity * random.uniform(0.95, 0.99))
        
        finishing = FinishingAndPacking(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'FIN-{fake.bothify(text="######")}',
            job_worker_name=fake.company(),
            issued_challan_quantity=int(challan_quantity),
            packed_quantity=packed_qty,
            rate=random.uniform(10, 30),
            user=user
        )
        finishing.save()
        return finishing

    def _create_dispatch(self, order, fake, user, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=110)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
        
        # Get quantities from previous step if available
        try:
            finishing = FinishingAndPacking.objects.filter(order=order).latest('issued_challan_date')
            quantity = finishing.packed_quantity
        except FinishingAndPacking.DoesNotExist:
            quantity = order.quantity * random.uniform(0.8, 0.9)
        
        dispatch = Dispatch(
            order=order,
            dispatch_date=date,
            dispatched_to=fake.company(),
            quantity=int(quantity),
            delivery_note=f'DN-{fake.bothify(text="######")}',
            invoice_number=f'INV-{fake.bothify(text="######")}',
            user=user
        )
        dispatch.save()
        return dispatch