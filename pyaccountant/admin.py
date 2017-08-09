from django.contrib import admin

from .models import (Account, Category,
                     Transaction, TransactionJournal)


admin.site.register(Account)
admin.site.register(TransactionJournal)
admin.site.register(Category)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('journal', 'account', 'opposing_account', 'amount')
    list_filter = ('account', 'opposing_account', 'journal__category')
