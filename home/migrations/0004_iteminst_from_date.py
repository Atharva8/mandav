# Generated by Django 3.1.6 on 2021-05-12 04:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20210512_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='iteminst',
            name='from_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
