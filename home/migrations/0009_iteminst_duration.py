# Generated by Django 3.1.6 on 2021-05-19 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_remove_item_rented'),
    ]

    operations = [
        migrations.AddField(
            model_name='iteminst',
            name='duration',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
