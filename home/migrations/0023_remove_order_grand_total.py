# Generated by Django 3.2.3 on 2021-06-06 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_alter_order_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='grand_total',
        ),
    ]
