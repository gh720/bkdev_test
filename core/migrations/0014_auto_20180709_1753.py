# Generated by Django 2.0.7 on 2018-07-09 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20180709_0711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerdiscount',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Customer'),
        ),
    ]