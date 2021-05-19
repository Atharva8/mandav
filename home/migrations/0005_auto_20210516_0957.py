# Generated by Django 3.1.6 on 2021-05-16 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_iteminst_from_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='price',
        ),
        migrations.AddField(
            model_name='item',
            name='price_by_day',
            field=models.PositiveIntegerField(default=0, verbose_name='Price by day(₹)'),
        ),
        migrations.AddField(
            model_name='item',
            name='price_by_hour',
            field=models.PositiveIntegerField(default=0, verbose_name='Price by hour(₹)'),
        ),
    ]