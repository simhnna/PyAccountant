# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-04 20:06
from __future__ import unicode_literals

from django.db import migrations


def migrate_to_new_schema(apps, schema_editor):
    TransactionJournal = apps.get_model('silverstrike', 'TransactionJournal')
    Transaction = apps.get_model('silverstrike', 'Transaction')
    Journal = apps.get_model('silverstrike', 'Journal')
    Split = apps.get_model('silverstrike', 'Split')
    
    for j in TransactionJournal.objects.all():
        journal = Journal.objects.create(title=j.title, date=j.date,
                notes=j.notes, transaction_type=j.transaction_type)
        for t in Transaction.objects.filter(journal=j):
            Split.objects.create(journal=journal,
                                 account=t.account,
                                 opposing_account=t.opposing_account,
                                 description=j.title,
                                 amount=t.amount,
                                 date=j.date,
                                 category=j.category)


class Migration(migrations.Migration):

    dependencies = [
        ('silverstrike', '0005_auto_20170904_2006'),
    ]

    operations = [
        migrations.RunPython(migrate_to_new_schema),
    ]
