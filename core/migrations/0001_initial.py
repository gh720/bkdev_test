# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-06 14:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='SourceLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src_lang', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='language',
            field=models.ManyToManyField(related_name='projects', to='core.SourceLanguage'),
        ),
        migrations.AddField(
            model_name='contributor',
            name='projects',
            field=models.ManyToManyField(related_name='contributors', to='core.Project'),
        ),
    ]