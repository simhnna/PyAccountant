import datetime

from django.http import JsonResponse

from .models import Account


def get_accounts(request, account_type):
    account_type = getattr(Account, account_type)
    accounts = list(Account.objects.filter(
        internal_type=account_type).values_list('name', flat=True))
    return JsonResponse(accounts, safe=False)


def get_accounts_balance(request, dstart, dend):
    delta = datetime.timedelta(days=3)
    dstart = datetime.datetime.strptime(dstart, '%Y-%m-%d') - delta
    dend = datetime.datetime.strptime(dend, '%Y-%m-%d') + delta
    dataset = []
    for account in Account.objects.filter(internal_type=Account.PERSONAL, show_on_dashboard=True):
        data = list(zip(*account.get_data_points(dstart, dend)))
        dataset.append({'name': account.name, 'data': data[1]})
    if dataset:
        labels = [datetime.datetime.strftime(x, '%d %b %Y') for x in data[0]]
    else:
        labels = []
    return JsonResponse({'labels': labels, 'dataset': dataset})
