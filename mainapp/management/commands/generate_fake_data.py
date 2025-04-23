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
    
    # Challan processing times
    FABRIC_CHALLAN_DAYS_MIN = 1
    FABRIC_CHALLAN_DAYS_MAX = 3
    
    DYEING_RECEIVE_DAYS_MIN = 2
    DYEING_RECEIVE_DAYS_MAX = 5
    
    CUTTING_RECEIVE_DAYS_MIN = 1
    CUTTING_RECEIVE_DAYS_MAX = 3
    
    STITCHING_RECEIVE_DAYS_MIN = 3
    STITCHING_RECEIVE_DAYS_MAX = 7
    
    EXTRA_WORK_RECEIVE_DAYS_MIN = 2
    EXTRA_WORK_RECEIVE_DAYS_MAX = 5
    
    # Material quantity factors
    FABRIC_QUANTITY_FACTOR_MIN = 1.1  # Need more fabric than final quantity
    FABRIC_QUANTITY_FACTOR_MAX = 1.3
    
    FABRIC_CHALLAN_FACTOR_MIN = 0.9  # Some fabric might be held back
    FABRIC_CHALLAN_FACTOR_MAX = 1.0
    
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
            order_date = fake.date_between(start_date=first_day, end_date=min(last_day, today)) # Create orders only up to today
            # order_date = fake.date_between(start_date=first_day, end_date=last_day) # Create orders for the entire month
            
            # Assign a random user from our list
            user = random.choice(users) if users else None
            
            order = Order(
                order_date=order_date,
                style_id=f'STY-{fake.bothify(text="??###")}',
                order_received_from=fake.company(),
                quantity=random.randint(self.ORDER_QUANTITY_MIN, self.ORDER_QUANTITY_MAX),
                size=random.choice(['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL', '5XL']),
                rate=random.randint(self.ORDER_RATE_MIN, self.ORDER_RATE_MAX),
                user=user
            )
            order.save()
            orders.append(order)
            self.stdout.write(f'Created order: {order} on {order.order_date} (User: {user.username})')
            
        # Generate complete lifecycle for some orders if requested
        if options['complete']:
            complete_orders = random.sample(orders, min(len(orders), max(1, num_orders // 2)))
            for order in complete_orders:
                self._generate_full_lifecycle(order, fake, users, last_day)
        else:
            # Otherwise, generate random stages
            for order in orders:
                # Randomly decide how far in the process this order should go
                stage = random.randint(0, 7)  # 0-7 for the 8 possible statuses
                if stage >= 1:
                    self._create_fabric_purchased(order, fake, users, last_day=last_day)
                if stage >= 2:
                    self._create_printing_and_dyeing(order, fake, users, last_day=last_day)
                if stage >= 3:
                    self._create_cloth_cutting(order, fake, users, last_day=last_day)
                if stage >= 4:
                    self._create_stitching(order, fake, users, last_day=last_day)
                if stage >= 5:
                    self._create_extra_work(order, fake, users, last_day=last_day)
                if stage >= 6:
                    self._create_finishing_and_packing(order, fake, users, last_day=last_day)
                if stage >= 7:
                    self._create_dispatch(order, fake, users, last_day=last_day)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated data for {num_orders} orders within {today.strftime("%B %Y")}'))

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
        
        # Add days for printing and dyeing (scaled)
        days_to_add = max(1, int(random.randint(self.PRINTING_DYEING_DAYS_MIN, 
                                               self.PRINTING_DYEING_DAYS_MAX) * time_compression))
        current_date += timedelta(days=days_to_add)
        if last_day and current_date > last_day.date():
            current_date = last_day.date()
        pd = self._create_printing_and_dyeing(order, fake, users, current_date)
        
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
            
        # Ensure challan date doesn't exceed month end
        challan_days = random.randint(self.FABRIC_CHALLAN_DAYS_MIN, self.FABRIC_CHALLAN_DAYS_MAX)
        challan_date = date + timedelta(days=challan_days)
        if last_day and challan_date > last_day.date():
            challan_date = last_day.date()
        
        quantity = order.quantity * random.uniform(self.FABRIC_QUANTITY_FACTOR_MIN, self.FABRIC_QUANTITY_FACTOR_MAX)
        challan_quantity = quantity * random.uniform(self.FABRIC_CHALLAN_FACTOR_MIN, self.FABRIC_CHALLAN_FACTOR_MAX)
        
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
            challan_number=f'CHN-{fake.bothify(text="######")}',
            issued_challan_date=challan_date,
            issued_challan_quantity=int(challan_quantity),
            user=user
        )
        fabric.save()
        self.stdout.write(f'Created fabric purchase record for order {order.id} (User: {user.username if user else "None"})')
        return fabric

    def _create_printing_and_dyeing(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=45)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Assign a random user
        user = random.choice(users) if users else None
            
        # Ensure receive date doesn't exceed month end
        receive_days = random.randint(self.DYEING_RECEIVE_DAYS_MIN, self.DYEING_RECEIVE_DAYS_MAX)
        receive_date = date + timedelta(days=receive_days)
        if last_day and receive_date > last_day.date():
            receive_date = last_day.date()
        
        # Get quantities from previous step if available
        try:
            fabric = FabricPurchased.objects.filter(order=order).latest('fabric_purchase_date')
            challan_quantity = fabric.issued_challan_quantity
        except FabricPurchased.DoesNotExist:
            challan_quantity = order.quantity * random.uniform(self.FABRIC_QUANTITY_FACTOR_MIN, self.FABRIC_QUANTITY_FACTOR_MAX)
        
        shrinkage = random.uniform(self.SHRINKAGE_MIN, self.SHRINKAGE_MAX)
        received_qty = int(challan_quantity * (1 - shrinkage/100))
        
        pd = PrintingAndDyeing(
            order=order,
            issued_challan_date=date,
            # issued_challan_number=f'PDC-{fake.bothify(text="######")}',
            dyer_printer_name=fake.company(),
            fabric_detail=random.choice(self.FABRIC_TYPES),
            fabric_length=f'{random.randint(40, 60)}"{random.choice(["", "/", "x"])}{random.randint(40, 60)}"',
            issued_challan_quantity=int(challan_quantity),
            shrinkage_in_percentage=shrinkage,
            received_quantity=received_qty,
            received_date=receive_date,
            received_challan_number=f'RCV-{fake.bothify(text="######")}',
            rate=random.uniform(self.DYEING_RATE_MIN, self.DYEING_RATE_MAX),
            user=user
        )
        pd.save()
        self.stdout.write(f'Created printing/dyeing record for order {order.id} (User: {user.username if user else "None"})')
        return pd

    def _create_cloth_cutting(self, order, fake, users, custom_date=None, last_day=None):
        if custom_date:
            date = custom_date
        else:
            max_date = last_day.date() if last_day else order.order_date + timedelta(days=60)
            date = fake.date_between(start_date=order.order_date, end_date=max_date)
            
        # Assign a random user
        user = random.choice(users) if users else None
            
        # Ensure receive date doesn't exceed month end
        receive_days = random.randint(self.CUTTING_RECEIVE_DAYS_MIN, self.CUTTING_RECEIVE_DAYS_MAX)
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
        received_qty = int(challan_quantity * random.uniform(self.CUTTING_YIELD_FACTOR_MIN, self.CUTTING_YIELD_FACTOR_MAX))
        
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
            
        # Ensure receive date doesn't exceed month end
        receive_days = random.randint(self.STITCHING_RECEIVE_DAYS_MIN, self.STITCHING_RECEIVE_DAYS_MAX)
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
        received_qty = int(challan_quantity * random.uniform(self.STITCHING_YIELD_FACTOR_MIN, self.STITCHING_YIELD_FACTOR_MAX))
        
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
            
        # Ensure receive date doesn't exceed month end
        receive_days = random.randint(self.EXTRA_WORK_RECEIVE_DAYS_MIN, self.EXTRA_WORK_RECEIVE_DAYS_MAX)
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
        received_qty = int(challan_quantity * random.uniform(self.EXTRA_WORK_YIELD_FACTOR_MIN, self.EXTRA_WORK_YIELD_FACTOR_MAX))
        
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
            challan_quantity = order.quantity * random.uniform(0.85, 0.95)
        
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
        self.stdout.write(f'Created dispatch record for order {order.id} (User: {user.username if user else "None"})')
        return dispatch