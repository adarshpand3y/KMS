# Generated by Django 5.1.6 on 2025-04-04 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_rename_quantity_extrawork_issued_challan_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stitching',
            name='extra_work_name',
        ),
    ]
