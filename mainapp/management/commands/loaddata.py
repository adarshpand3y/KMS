# mainapp/management/commands/loaddata.py
from django.core.management.base import BaseCommand
import json
from mainapp.models import Order, FabricPurchased, PrintingAndDyeing, ClothCutting, Stitching, FinishingAndPacking, Dispatch
from django.contrib.auth.models import User
import datetime

class Command(BaseCommand):
    help = 'Load fake data from JSON file into database'

    def handle(self, *args, **kwargs):
        self.loaddata()

    def loaddata(self, filename='fake_data.json'):
        """Load data from JSON file into Django models."""
        with open(filename, 'r') as f:
            data = json.load(f)

        for entry in data:
            # Load Order
            order_data = entry['order']
            order = Order.objects.create(
                style_id=order_data['style_id'],
                order_received_from=order_data['order_received_from'],
                quantity=order_data['quantity'],
                rate=order_data['rate'],
                user=User.objects.get(id=order_data['user_id']),
            )

            # Load FabricPurchased (similarly for other models)
            # ...

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded data from {filename}'))
