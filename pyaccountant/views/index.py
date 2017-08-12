from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.views import generic


from pyaccountant.lib import last_day_of_month
from pyaccountant.models import Account, RecurringTransaction, Transaction


def _get_account_info(dstart, dend, account=None):
    context = dict()
    queryset = Transaction.objects.filter(
        journal__date__gte=dstart,
        journal__date__lte=dend)
    if account:
        queryset = queryset.filter(account=account)
    context['income'] = abs(queryset.filter(
        account__internal_type=Account.PERSONAL,
        opposing_account__internal_type=Account.REVENUE).aggregate(
            models.Sum('amount'))['amount__sum'] or 0)

    context['expenses'] = abs(queryset.filter(
        account__internal_type=Account.PERSONAL,
        opposing_account__internal_type=Account.EXPENSE).aggregate(
            models.Sum('amount'))['amount__sum'] or 0)
    context['difference'] = context['income'] - context['expenses']
    return context


class IndexView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'pyaccountant/index.html'

    def get_context_data(self, **kwargs):
        first = date.today().replace(day=1)
        last = last_day_of_month(first)
        context = super().get_context_data(**kwargs)
        context['menu'] = 'home'
        queryset = Transaction.objects.filter(account__internal_type=Account.PERSONAL)
        context['balance'] = queryset.aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        context.update(_get_account_info(first, last))
        context['accounts'] = Account.objects.filter(internal_type=Account.PERSONAL,
                                                     show_on_dashboard=True)
        context['due_transactions'] = RecurringTransaction.objects.due_in_month()
        context['transactions'] = Transaction.objects.transactions()[:10]
        return context
