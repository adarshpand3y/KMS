# Generated by Django 5.1.6 on 2025-04-23 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0018_alter_printinganddyeing_balance_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printinganddyeing',
            name='received_challan_number',
            field=models.CharField(help_text='Each line represents the box number', max_length=50),
        ),
    ]
