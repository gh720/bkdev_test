# Generated by Django 2.0.7 on 2018-07-08 21:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20180709_0131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='customer_discount',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.CustomerDiscount'),
        ),
    ]
