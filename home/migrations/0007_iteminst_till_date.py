# Generated by Django 3.1.6 on 2021-05-16 04:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_auto_20210516_1001'),
    ]

    operations = [
        migrations.AddField(
            model_name='iteminst',
            name='till_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
