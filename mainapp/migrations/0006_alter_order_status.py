# Generated by Django 5.1.6 on 2025-03-06 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Fabric Purchased', 'Fabric Purchased'), ('Printing and Dyeing', 'Printing and Dyeing'), ('Cloth Cutting', 'Cloth Cutting'), ('Stitching', 'Stitching'), ('Finishing and Packing', 'Finishing and Packing'), ('Dispatched', 'Dispatched')], default='Pending', max_length=50),
        ),
    ]
