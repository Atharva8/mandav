# Generated by Django 3.1.6 on 2021-02-27 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_auto_20210227_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='gst_status',
            field=models.CharField(choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid', max_length=10),
        ),
    ]
