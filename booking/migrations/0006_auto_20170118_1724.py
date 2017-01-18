# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-18 16:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_auto_20170118_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='agreement',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booking', to='booking.Agreement', verbose_name='Convention'),
        ),
    ]
