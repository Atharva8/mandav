# Generated by Django 3.1.6 on 2021-05-18 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_iteminst_till_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='rented',
        ),
    ]
