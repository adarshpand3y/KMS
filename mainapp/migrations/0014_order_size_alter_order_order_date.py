# Generated by Django 5.1.6 on 2025-04-20 14:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0013_alter_extrawork_options_extrawork_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='size',
            field=models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('2XL', '2XL'), ('3XL', '3XL'), ('4XL', '4XL'), ('5XL', '5XL')], default='S', max_length=3),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
