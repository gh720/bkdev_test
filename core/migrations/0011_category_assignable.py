# Generated by Django 2.0.7 on 2018-07-08 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20180709_0222'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='assignable',
            field=models.BooleanField(default=True),
        ),
    ]