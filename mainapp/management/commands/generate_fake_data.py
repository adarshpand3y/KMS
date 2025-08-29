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
    PrintingAndDyeingSent,
    PrintingAndDyeingReceived,
    ClothCutting,
    Stitching,
    ExtraWork,
    FinishingAndPacking,
    Dispatch
)

class Command(BaseCommand):
    help = 'Generates fake data for clothing production management system'
    
    # Configuration variables
    DEFAULT_NUM_ORDERS = 100
    DEFAULT_NUM_USERS = 5  # Default number of users to create
    
    # Sample user roles
    USER_ROLES = ['manager', 'production_supervisor', 'quality_control', 'inventory', 'logistics']
    
    # Fabric details options
    FABRIC_TYPES = ['Cotton', 'Linen', 'Silk', 'Wool', 'Polyester', 'Rayon']
    
    # Extra work options
    EXTRA_WORK_TYPES = ['Embroidery', 'Beading', 'Sequins', 'Appliqué', 'Pleating', 'Printing']
    
    # Order parameters
    ORDER_QUANTITY_MIN = 100
    ORDER_QUANTITY_MAX = 500
    ORDER_RATE_MIN = 100
    ORDER_RATE_MAX = 500
    
    # Production timeline parameters (days)
    FABRIC_PURCHASE_DAYS_MIN = 1
    FABRIC_PURCHASE_DAYS_MAX = 3
    
    PRINTING_DYEING_DAYS_MIN = 3
    PRINTING_DYEING_DAYS_MAX = 7
    
    CLOTH_CUTTING_DAYS_MIN = 2
    CLOTH_CUTTING_DAYS_MAX = 4
    
    STITCHING_DAYS_MIN = 4
    STITCHING_DAYS_MAX = 10
    
    EXTRA_WORK_DAYS_MIN = 2
    EXTRA_WORK_DAYS_MAX = 5
    
    FINISHING_PACKING_DAYS_MIN = 1
    FINISHING_PACKING_DAYS_MAX = 3
    
    DISPATCH_DAYS_MIN = 1
    DISPATCH_DAYS_MAX = 2
    
    # Material quantity factors
    FABRIC_QUANTITY_FACTOR_MIN = 1.1  # Need more fabric than final quantity
    FABRIC_QUANTITY_FACTOR_MAX = 1.3
    
    SHRINKAGE_MIN = 1.0  # Percentage
    SHRINKAGE_MAX = 10.0
    
    CUTTING_YIELD_FACTOR_MIN = 0.9  # Material lost in cutting
    CUTTING_YIELD_FACTOR_MAX = 0.98
    
    STITCHING_YIELD_FACTOR_MIN = 0.92  # Rejected pieces in stitching
    STITCHING_YIELD_FACTOR_MAX = 0.98
    
    EXTRA_WORK_YIELD_FACTOR_MIN = 0.95  # Pieces passing extra work
    EXTRA_WORK_YIELD_FACTOR_MAX = 0.99
    
    FINISHING_YIELD_FACTOR_MIN = 0.95  # Final inspection rejection rate
    FINISHING_YIELD_FACTOR_MAX = 0.99
    
    # Price ranges
    FABRIC_RATE_MIN = 50
    FABRIC_RATE_MAX = 200
    
    DYEING_RATE_MIN = 30
    DYEING_RATE_MAX = 100
    
    CUTTING_RATE_MIN = 10
    CUTTING_RATE_MAX = 50
    
    STITCHING_RATE_MIN = 50
    STITCHING_RATE_MAX = 200
    
    EXTRA_WORK_RATE_MIN = 20
    EXTRA_WORK_RATE_MAX = 100
    
    FINISHING_RATE_MIN = 10
    FINISHING_RATE_MAX = 30

    def add_arguments(self, parser):
        parser.add_argument('--orders', type=int, default=self.DEFAULT_NUM_ORDERS, help='Number of orders to generate')
        parser.add_argument('--user', type=str, default=None, help='Username to associate with records')
        parser.add_argument('--complete', action='store_true', help='Generate complete lifecycle for some orders')
        parser.add_argument('--users', type=int, default=self.DEFAULT_NUM_USERS, help='Number of sample users to create')

    def handle(self, *args, **options):
        fake = Faker()
        num_orders = options['orders']
        specified_user = None
        
        # Create sample users or get the specified user
        users = []
        
        if options['user']:
            try:
                specified_user = User.objects.get(username=options['user'])
                self.stdout.write(self.style.SUCCESS(f'Using specified user: {specified_user.username}'))
                users.append(specified_user)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'User {options["user"]} not found.'))
        
        # Create sample users if no specific user was provided or add more users
        if not options['user'] or (options['user'] and options['users'] > 1):
            num_users = options['users']
            self.stdout.write(f'Creating {num_users} sample users...')
            
            # Create admin user if it doesn't exist
            try:
                admin_user = User.objects.get(username='admin')
                self.stdout.write(f'Admin user already exists')
                if not users or admin_user.id != specified_user.id:
                    users.append(admin_user)
            except User.DoesNotExist:
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
                self.stdout.write(f'Created admin user: admin')
                users.append(admin_user)
            
            # Create regular users with roles in their usernames
            for i in range(num_users - (1 if 'admin' in [u.username for u in users] else 0)):
                role = self.USER_ROLES[i % len(self.USER_ROLES)]
                username = f"{role}_{i+1}"
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    self.stdout.write(f'User {username} already exists')
                else:
                    user = User.objects.create_user(
                        username=username,
                        email=f"{username}@example.com",
                        password=f"{username}123",
                        first_name=fake.first_name(),
                        last_name=fake.last_name()
                    )
                    self.stdout.write(f'Created user: {username}')
                
                if not users or user.id not in [u.id for u in users]:
                    users.append(user)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created/loaded {len(users)} users'))
        
        # Get current month's date range
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        last_day = datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        
        # Create orders within the current month
        self.stdout.write(f'Generating {num_orders} orders for the current month ({today.strftime("%B %Y")})...')
        orders = []
        
        for _ in range(num_orders):
            # Create a random date within the current month
            order_date = fake.date_between(start_date=first_day, end_date=min(last_day, today))
            
            # Assign a random user from our list
            user = random.choice(users) if users else None
            
            # Generate size distribution
            size_quantities = self._generate_size_distribution(
                random.randint(self.ORDER_QUANTITY_MIN, self.ORDER_QUANTITY_MAX)
            )
            
            order = Order(
                order_date=order_date,
                po_number=f'PO-{fake.bothify(text="######")}',
                style_id=f'STY-{fake.bothify(text="??###")}',
                order_received_from=fake.company(),
                rate=random.randint(self.ORDER_RATE_MIN, self.ORDER_RATE_MAX),
                user=user,
                **size_quantities
            )
            order.save()  # This will calculate total quantity and amount
            orders.append(order)
            self.stdout.write(f'Created order: {order} on {order.order_date} (User: {user.username if user else "None"})')
            
        # Generate complete lifecycle for some orders if requested
        if options['complete']:
            complete_orders = random.sample(orders, min(len(orders), max(1, num_orders // 2)))
            for order in complete_orders:
                self._generate_full_lifecycle(order, fake, users, last_day)
        else:
            # Otherwise, generate random stages
            for order in orders:
                # Randomly decide how far in the process this order should go
                stage = random.randint(0, 8)  # 0-8 for the 9 possible statuses
                if stage >= 1:
                    self._create_fabric_purchased(order, fake, users, last_day=last_day)
                if stage >= 2:
                    printing_sent = self._create_printing_and_dyeing_sent(order, fake, users, last_day=last_day)
                if stage >= 3 and 'printing_sent' in locals():
                    self._create_printing_and_dyeing_received(order, printing_sent, fake, users, last_day=last_day)
                if stage >= 4:
                    self._create_cloth_cutting(order, fake, users, last_day=last_day)
                if stage >= 5:
                    self._create_stitching(order, fake, users, last_day=last_day)
                if stage >= 6:
                    self._create_extra_work(order, fake, users, last_day=last_day)
                if stage >= 7:
                    self._create_finishing_and_packing(order, fake, users, last_day=last_day)
                if stage >= 8:
                    self._create_dispatch(order, fake, users, last_day=last_day)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated data for {num_orders} orders within {today.strftime("%B %Y")}'))

    def _generate_size_distribution(self, total_quantity):
        """Generate realistic size distribution for order quantities"""
        # Common size distribution weights (M and L are most common)
        size_weights = {
            'quantity_xs': 0.05,
            'quantity_s': 0.15,
            'quantity_m': 0.25,
            'quantity_l': 0.25,
            'quantity_xl': 0.15,
            'quantity_2xl': 0.08,
            'quantity_3xl': 0.04,
            'quantity_4xl': 0.02,
            'quantity_5xl': 0.01,
            'quantity_6xl': 0.005,
            'quantity_7xl': 0.005,
            'quantity_8xl': 0,
            'quantity_9xl': 0,
            'quantity_10xl': 0
        }
        
        quantities = {}
        remaining = total_quantity
        
        # Distribute quantities based on weights
        for size_field, weight in size_weights.items():
            if remaining <= 0:
                quantities[size_field] = 0
            else:
                qty = int(total_quantity * weight)
                # Add some randomness
                qty = max(0, qty + random.randint(-5, 5))
                qty = min(qty, remaining)
                quantities[size_field] = qty
                remaining -= qty
        
        # Distribute any remaining quantity to popular sizes
        popular_sizes = ['quantity_m', 'quantity_l', 'quantity_xl']
        while remaining > 0:
            size = random.choice(popular_sizes)
            quantities[size] += 1
            remaining -= 1
            
        return quantities

    def _generate_full_lifecycle(self, order, fake, users, last_day=None):
        """Generate a complete lifecycle for an order with realistic dates"""
        self.stdout.write(f'Generating complete lifecycle for order {order}')
        
        # Start date is the order date
        current_date = order.order_date
        remaining_days = (last_day.date() - current_date).days if last_day else 30
        
        # If very few days remain, compress the timeline
        time_compression = max(1, remaining_days / 30)  # Scale factor for timeline compression
        
        # Add days for fabric purchase (scaled)
        days_to_add = max(1, int(random.randint(self.FABRIC_PURCHASE_DAYS_MIN, 
                                               self.FABRIC_PURCHASE_DAYS_MAX) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        fabric = self._create_fabric_purchased(order, fake, users, current_date)
        
        # Add days for printing and dyeing sent (scaled)
        days_to_add = max(1, int(random.randint(self.PRINTING_DYEING_DAYS_MIN, 
                                               self.PRINTING_DYEING_DAYS_MAX) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        printing_sent = self._create_printing_and_dyeing_sent(order, fake, users, current_date)
        
        # Add days for printing and dyeing received (scaled)
        days_to_add = max(1, int(random.randint(2, 5) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        printing_received = self._create_printing_and_dyeing_received(order, printing_sent, fake, users, current_date)
        
        # Add days for cloth cutting (scaled)
        days_to_add = max(1, int(random.randint(self.CLOTH_CUTTING_DAYS_MIN, 
                                               self.CLOTH_CUTTING_DAYS_MAX) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        cutting = self._create_cloth_cutting(order, fake, users, current_date)
        
        # Add days for stitching (scaled)
        days_to_add = max(1, int(random.randint(self.STITCHING_DAYS_MIN, 
                                               self.STITCHING_DAYS_MAX) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        stitching = self._create_stitching(order, fake, users, current_date)
        
        # Add days for extra work (scaled)
        days_to_add = max(1, int(random.randint(self.EXTRA_WORK_DAYS_MIN, 
                                               self.EXTRA_WORK_DAYS_MAX) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        extra = self._create_extra_work(order, fake, users, current_date)
        
        # Add days for finishing and packing (scaled)
        days_to_add = max(1, int(random.randint(self.FINISHING_PACKING_DAYS_MIN, 
                                               self.FINISHING_PACKING_DAYS_MAX) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        finishing = self._create_finishing_and_packing(order, fake, users, current_date)
        
        # Add days for dispatch (scaled)
        days_to_add = max(1, int(random.randint(self.DISPATCH_DAYS_MIN, 
                                               self.DISPATCH_DAYS_MAX) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        dispatch = self._create_dispatch(order, fake, users, current_date)
        
        self.stdout.write(self.style.SUCCESS(f'Completed full lifecycle for order {order}'))
        
    def _create_fabric_purchased(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=30)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Assign a random user
        user = random.choice(users) if users else None
        
        quantity = order.quantity * random.uniform(self.FABRIC_QUANTITY_FACTOR_MIN, self.FABRIC_QUANTITY_FACTOR_MAX)
        
        fabric = FabricPurchased(
            order=order,
            fabric_purchase_date=date,
            purchased_from=fake.company(),
            quantity=int(quantity),
            rate=random.uniform(self.FABRIC_RATE_MIN, self.FABRIC_RATE_MAX),
            invoice_number=f'INV-{fake.bothify(text="######")}',
            fabric_detail=random.choice(self.FABRIC_TYPES),
            fabric_length=f'{random.randint(40, 60)}"{random.choice(["", "/", "x"])}{random.randint(40, 60)}"',
            fabric_dyer=fake.company(),
            user=user
        )
        fabric.save()
        self.stdout.write(f'Created fabric purchase record for order {order.id} (User: {user.username if user else "None"})')
        return fabric

    def _create_printing_and_dyeing_sent(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=45)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Assign a random user
        user = random.choice(users) if users else None
        
        # Get quantities from previous step if available
        try:
            fabric = FabricPurchased.objects.filter(order=order).latest('fabric_purchase_date')
            challan_quantity = int(fabric.quantity * random.uniform(0.9, 1.0))
        except FabricPurchased.DoesNotExist:
            challan_quantity = int(order.quantity * random.uniform(self.FABRIC_QUANTITY_FACTOR_MIN, self.FABRIC_QUANTITY_FACTOR_MAX))
        
        printing_sent = PrintingAndDyeingSent(
            order=order,
            issued_challan_date=date,
            dyer_printer_name=fake.company(),
            fabric_detail=random.choice(self.FABRIC_TYPES),
            fabric_length=f'{random.randint(40, 60)}"{random.choice(["", "/", "x"])}{random.randint(40, 60)}"',
            issued_challan_quantity=challan_quantity,
            user=user
        )
        printing_sent.save()
        self.stdout.write(f'Created printing/dyeing sent record for order {order.id} (User: {user.username if user else "None"})')
        return printing_sent

    def _create_printing_and_dyeing_received(self, order, printing_sent, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else printing_sent.issued_challan_date + timedelta(days=10)
            date = fake.date_between(start_date=printing_sent.issued_challan_date, end_date=max_date)
            
        # Assign a random user
        user = random.choice(users) if users else None
        
        shrinkage = random.uniform(self.SHRINKAGE_MIN, self.SHRINKAGE_MAX)
        
        printing_received = PrintingAndDyeingReceived(
            order=order,
            printing_and_dyeing_sent=printing_sent,
            shrinkage_in_percentage=shrinkage,
            received_date=date,
            received_challan_number=f'RCV-{fake.bothify(text="######")}',
            rate=random.uniform(self.DYEING_RATE_MIN, self.DYEING_RATE_MAX),
            user=user
        )
        printing_received.save()
        self.stdout.write(f'Created printing/dyeing received record for order {order.id} (User: {user.username if user else "None"})')
        return printing_received

    def _create_cloth_cutting(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=60)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Assign a random user
        user = random.choice(users) if users else None
            
        # Get quantities from previous step if available
        try:
            printing_received = PrintingAndDyeingReceived.objects.filter(order=order).latest('received_date')
            challan_quantity = printing_received.received_quantity
        except PrintingAndDyeingReceived.DoesNotExist:
            challan_quantity = int(order.quantity * random.uniform(1.0, 1.1))
        
        # Some material may be lost in cutting
        received_qty = int(challan_quantity * random.uniform(self.CUTTING_YIELD_FACTOR_MIN, self.CUTTING_YIELD_FACTOR_MAX))
        
        receive_date = date + timedelta(days=random.randint(1, 3))
        if last_day and receive_date > last_day.date():
            receive_date = last_day.date()
        
        cutting = ClothCutting(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'CUT-{fake.bothify(text="######")}',
            job_worker_name=fake.company(),
            fabric_detail=random.choice(self.FABRIC_TYPES),
            fabric_length=f'{random.randint(40, 60)}"{random.choice(["", "/", "x"])}{random.randint(40, 60)}"',
            issued_challan_quantity=int(challan_quantity),
            received_quantity=received_qty,
            received_date=receive_date,
            received_challan_number=f'RCV-{fake.bothify(text="######")}',
            rate=random.uniform(self.CUTTING_RATE_MIN, self.CUTTING_RATE_MAX),
            user=user
        )
        cutting.save()
        self.stdout.write(f'Created cloth cutting record for order {order.id} (User: {user.username if user else "None"})')
        return cutting

    def _create_stitching(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=75)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Assign a random user
        user = random.choice(users) if users else None
        
        # Get quantities from previous step if available
        try:
            cutting = ClothCutting.objects.filter(order=order).latest('issued_challan_date')
            challan_quantity = cutting.received_quantity
        except ClothCutting.DoesNotExist:
            challan_quantity = int(order.quantity * random.uniform(0.95, 1.05))
        
        # Some pieces may be rejected during stitching
        received_qty = int(challan_quantity * random.uniform(self.STITCHING_YIELD_FACTOR_MIN, self.STITCHING_YIELD_FACTOR_MAX))
        
        receive_date = date + timedelta(days=random.randint(3, 7))
        if last_day and receive_date > last_day.date():
            receive_date = last_day.date()
        
        stitching = Stitching(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'STI-{fake.bothify(text="######")}',
            job_worker_name=fake.company(),
            issued_challan_quantity=int(challan_quantity),
            received_quantity=received_qty,
            received_date=receive_date,
            rate=random.uniform(self.STITCHING_RATE_MIN, self.STITCHING_RATE_MAX),
            user=user
        )
        stitching.save()
        self.stdout.write(f'Created stitching record for order {order.id} (User: {user.username if user else "None"})')
        return stitching

    def _create_extra_work(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=90)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Assign a random user
        user = random.choice(users) if users else None
        
        # Get quantities from previous step if available
        try:
            stitching = Stitching.objects.filter(order=order).latest('issued_challan_date')
            challan_quantity = stitching.received_quantity
        except Stitching.DoesNotExist:
            challan_quantity = int(order.quantity * random.uniform(0.9, 1.0))
        
        # Most pieces should pass extra work
        received_qty = int(challan_quantity * random.uniform(self.EXTRA_WORK_YIELD_FACTOR_MIN, self.EXTRA_WORK_YIELD_FACTOR_MAX))
        
        receive_date = date + timedelta(days=random.randint(2, 5))
        if last_day and receive_date > last_day.date():
            receive_date = last_day.date()
        
        extra_work = ExtraWork(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'EXT-{fake.bothify(text="######")}',
            job_worker_name=fake.company(),
            extra_work_name=random.choice(self.EXTRA_WORK_TYPES),
            issued_challan_quantity=int(challan_quantity),
            received_quantity=received_qty,
            received_date=receive_date,
            rate=random.uniform(self.EXTRA_WORK_RATE_MIN, self.EXTRA_WORK_RATE_MAX),
            user=user
        )
        extra_work.save()
        self.stdout.write(f'Created extra work record for order {order.id} (User: {user.username if user else "None"})')
        return extra_work

    def _create_finishing_and_packing(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=100)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
        
        # Assign a random user
        user = random.choice(users) if users else None
        
        # Get quantities from previous step if available
        try:
            extra_work = ExtraWork.objects.filter(order=order).latest('issued_challan_date')
            challan_quantity = extra_work.received_quantity
        except ExtraWork.DoesNotExist:
            challan_quantity = int(order.quantity * random.uniform(0.85, 0.95))
        
        # Some pieces may be rejected during final inspection
        packed_qty = int(challan_quantity * random.uniform(self.FINISHING_YIELD_FACTOR_MIN, self.FINISHING_YIELD_FACTOR_MAX))
        
        finishing = FinishingAndPacking(
            order=order,
            issued_challan_date=date,
            issued_challan_number=f'FIN-{fake.bothify(text="######")}',
            job_worker_name=fake.company(),
            issued_challan_quantity=int(challan_quantity),
            packed_quantity=packed_qty,
            rate=random.uniform(self.FINISHING_RATE_MIN, self.FINISHING_RATE_MAX),
            user=user
        )
        finishing.save()
        self.stdout.write(f'Created finishing/packing record for order {order.id} (User: {user.username if user else "None"})')
        return finishing

    def _create_dispatch(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=110)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
        
        # Assign a random user
        user = random.choice(users) if users else None
        
        # Get quantities from previous step if available
        try:
            finishing = FinishingAndPacking.objects.filter(order=order).latest('issued_challan_date')
            quantity = finishing.packed_quantity
        except FinishingAndPacking.DoesNotExist:
            quantity = int(order.quantity * random.uniform(0.8, 0.9))
        
        # Generate box details for the shipment
        num_boxes = random.randint(1, max(1, quantity // 50))
        box_details = []
        remaining_qty = quantity
        
        for i in range(num_boxes):
            if i == num_boxes - 1:  # Last box gets remaining quantity
                box_qty = remaining_qty
            else:
                box_qty = random.randint(1, min(remaining_qty, quantity // num_boxes + 10))
            box_details.append(f"Box {i+1}: {box_qty} pieces")
            remaining_qty -= box_qty
        
        dispatch = Dispatch(
            order=order,
            dispatch_date=date,
            dispatched_to=fake.company(),
            quantity=int(quantity),
            delivery_note=f'DN-{fake.bothify(text="######")}',
            invoice_number=f'INV-{fake.bothify(text="######")}',
            box_details="\n".join(box_details),
            user=user
        )
        dispatch.save()
        self.stdout.write(f'Created dispatch record for order {order.id} (User: {user.username if user else "None"})')
        return dispatch