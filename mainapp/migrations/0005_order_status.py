# Generated by Django 5.1.6 on 2025-03-06 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_alter_order_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('FABRIC_PURCHASED', 'Fabric Purchased'), ('PRINTING_AND_DYEING', 'Printing and Dyeing'), ('CLOTH_CUTTING', 'Cloth Cutting'), ('STITCHING', 'Stitching'), ('FINISHING_AND_PACKING', 'Finishing and Packing'), ('DISPATCH', 'Dispatched')], default='PENDING', max_length=50),
        ),
    ]
