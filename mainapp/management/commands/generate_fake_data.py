from django.core.management.base import BaseCommand
import json
import random
import datetime
from faker import Faker
from django.contrib.auth.models import User
from mainapp.models import Order, FabricPurchased, PrintingAndDyeing, ClothCutting, Stitching, FinishingAndPacking, Dispatch

fake = Faker()

class Command(BaseCommand):
    help = 'Generates fake data and dumps it to a JSON file'

    def handle(self, *args, **kwargs):
        self.generate_fake_data()

    def generate_fake_user(self):
        """Create a fake user."""
        user = User.objects.create_user(username=fake.user_name(), email=fake.email(), password='password')
        return user

    def generate_fake_order(self, user):
        """Create a fake order."""
        order = Order(
            style_id=fake.uuid4(),
            order_received_from=fake.company(),
            quantity=random.randint(1, 100),
            rate=random.randint(100, 500),
            user=user
        )
        order.save()
        return order

    def generate_random_date_this_month(self):
        """Generate a random date within the current month."""
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today.replace(day=28) + datetime.timedelta(days=4)  # To ensure we get the last day of the month
        last_day_of_month = last_day_of_month - datetime.timedelta(days=last_day_of_month.day)  # Adjust to the last day of the month
        
        random_day = random.randint(first_day_of_month.day, last_day_of_month.day)
        return today.replace(day=random_day)

    def generate_fake_fabric_purchased(self, order, user):
        """Create fake fabric purchased for an order."""
        fabric = FabricPurchased(
            order=order,
            purchased_from=fake.company(),
            quantity=random.randint(50, 200),
            rate=random.uniform(20.0, 50.0),
            invoice_number=fake.uuid4(),
            fabric_detail=fake.word(),
            fabric_length=fake.word(),
            fabric_dyer=fake.name(),
            challan_number=fake.lexify(text='?' * 10),
            issued_challan_quantity=random.randint(50, 200),
            user=user
        )
        fabric.save()
        return fabric

    def generate_fake_printing_and_dyeing(self, order, user):
        """Create fake printing and dyeing for an order."""
        print_dyeing = PrintingAndDyeing(
            order=order,
            dyer_printer_name=fake.name(),
            fabric_detail=fake.word(),
            fabric_length=fake.word(),
            issued_challan_quantity=random.randint(50, 200),
            shrinkage_in_percentage=random.uniform(5.0, 10.0),
            received_quantity=random.randint(45, 190),
            rate=random.uniform(10.0, 25.0),
            issued_challan_number=fake.lexify(text='?' * 10),
            received_challan_number=fake.lexify(text='?' * 10),
            user=user
        )
        print_dyeing.save()
        return print_dyeing

    def generate_fake_cloth_cutting(self, order, user):
        """Create fake cloth cutting for an order."""
        cutting = ClothCutting(
            order=order,
            job_worker_name=fake.name(),
            fabric_detail=fake.word(),
            fabric_length=fake.word(),
            issued_challan_quantity=random.randint(50, 150),
            received_quantity=random.randint(50, 150),
            rate=random.uniform(15.0, 30.0),
            issued_challan_number=fake.lexify(text='?' * 10),
            received_challan_number=fake.lexify(text='?' * 10),
            user=user
        )
        cutting.save()
        return cutting

    def generate_fake_stitching(self, order, user):
        """Create fake stitching for an order."""
        stitching = Stitching(
            order=order,
            job_worker_name=fake.name(),
            extra_work_name=fake.word(),
            issued_challan_quantity=random.randint(50, 100),
            received_quantity=random.randint(50, 100),
            rate=random.uniform(10.0, 25.0),
            issued_challan_number=fake.lexify(text='?' * 10),
            # received_challan_number=fake.lexify(text='?' * 10),
            user=user
        )
        stitching.save()
        return stitching

    def generate_fake_finishing_and_packing(self, order, user):
        """Create fake finishing and packing for an order."""
        finishing = FinishingAndPacking(
            order=order,
            job_worker_name=fake.name(),
            issued_challan_quantity=random.randint(50, 100),
            packed_quantity=random.randint(40, 100),
            rate=random.uniform(10.0, 30.0),
            issued_challan_number=fake.lexify(text='?' * 10),
            user=user
        )
        finishing.save()
        return finishing

    def generate_fake_dispatch(self, order, user):
        """Create fake dispatch for an order."""
        dispatch = Dispatch(
            order=order,
            dispatched_to=fake.company(),
            quantity=order.quantity,
            invoice_number=fake.uuid4(),
            delivery_note=fake.uuid4(),
            dispatch_date=self.generate_random_date_this_month(),  # Randomized dispatch date within this month
            user=user
        )
        dispatch.save()
        return dispatch

    def generate_fake_data(self, num_users=5, num_orders=10):
        """Generate fake data for users and orders and dump into a JSON file."""
        data = []
        for _ in range(num_users):
            user = self.generate_fake_user()
            for _ in range(num_orders):
                order = self.generate_fake_order(user)
                fabric = self.generate_fake_fabric_purchased(order, user)
                print_dyeing = self.generate_fake_printing_and_dyeing(order, user)
                cutting = self.generate_fake_cloth_cutting(order, user)
                stitching = self.generate_fake_stitching(order, user)
                finishing = self.generate_fake_finishing_and_packing(order, user)
                dispatch = self.generate_fake_dispatch(order, user)

                data.append({
                    'order': {
                        'style_id': order.style_id,
                        'order_received_from': order.order_received_from,
                        'quantity': order.quantity,
                        'rate': order.rate,
                        'user_id': order.user.id,
                    },
                    # Include other fields for fabric, print_dyeing, etc.
                })

        # Dump data into JSON file
        with open('fake_data.json', 'w') as f:
            json.dump(data, f, default=str, indent=4)
        self.stdout.write(self.style.SUCCESS('Successfully generated fake data and dumped it to fake_data.json'))
