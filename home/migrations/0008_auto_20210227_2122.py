# Generated by Django 3.1.6 on 2021-02-27 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_order_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(default='Incomplete', max_length=10),
        ),
    ]
