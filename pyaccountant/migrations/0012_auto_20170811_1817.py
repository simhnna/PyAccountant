# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-11 18:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyaccountant', '0011_importconfiguration_default_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importconfiguration',
            name='name',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
