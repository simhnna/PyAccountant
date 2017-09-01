# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-01 07:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('silverstrike', '0003_auto_20170823_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionjournal',
            name='transaction_type',
            field=models.IntegerField(choices=[(1, 'Deposit'), (2, 'Withdrawl'), (3, 'Transfer'), (4, 'Reconcile')]),
        ),
    ]
