# Generated by Django 5.1.6 on 2025-04-04 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0009_alter_order_status_extrawork'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extrawork',
            name='style_id',
        ),
    ]
