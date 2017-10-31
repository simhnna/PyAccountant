from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from silverstrike.forms import DepositForm, TransactionFormSet, TransferForm, WithdrawForm
from silverstrike.models import Account, Split, Transaction


class TransactionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Transaction
    context_object_name = 'transaction'


class TransactionDeleteView(LoginRequiredMixin, generic.edit.DeleteView):
    model = Transaction
    success_url = reverse_lazy('accounts')


class TransactionIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'silverstrike/transaction_overview.html'
    context_object_name = 'transactions'
    model = Split
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().filter(account__account_type=Account.PERSONAL)

        if 'category' in self.request.GET:
            queryset = queryset.filter(category_id=self.request.GET['category'])
        if 'account' in self.request.GET:
            queryset = queryset.filter(account_id=self.request.GET['account'])
        else:
            queryset = queryset.exclude(transaction__transaction_type=Transaction.TRANSFER,
                                        amount__gt=0)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'transactions'
        context['submenu'] = 'all'
        return context


class TransferCreate(LoginRequiredMixin, generic.edit.CreateView):
    model = Transaction
    form_class = TransferForm
    template_name = 'silverstrike/transaction_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'transactions'
        context['submenu'] = 'transfer'
        return context


class TransactionUpdateView(LoginRequiredMixin, generic.edit.UpdateView):
    template_name = 'silverstrike/transaction_edit.html'
    model = Transaction

    def get_initial(self):
        initial = super().get_initial()
        self.transaction = Split.objects.get(transaction_id=self.kwargs.get('pk'), amount__gt=0)
        initial['source_account'] = self.transaction.opposing_account.pk
        initial['destination_account'] = self.transaction.account.pk
        if self.object.transaction_type == Transaction.WITHDRAW:
            initial['destination_account'] = self.transaction.account
        elif self.object.transaction_type == Transaction.DEPOSIT:
            initial['source_account'] = self.transaction.opposing_account
        initial['amount'] = self.transaction.amount
        initial['category'] = self.transaction.category
        initial['value_date'] = self.transaction.date
        return initial

    def get_queryset(self):
        queryset = super(TransactionUpdateView, self).get_queryset()
        return queryset.exclude(transaction_type=Transaction.SYSTEM)

    def get_form_class(self):
        if self.object.transaction_type == Transaction.WITHDRAW:
            return WithdrawForm
        elif self.object.transaction_type == Transaction.DEPOSIT:
            return DepositForm
        else:
            return TransferForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'transactions'
        return context


class WithdrawCreate(TransferCreate):
    form_class = WithdrawForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submenu'] = 'withdraw'
        return context


class DepositCreate(TransferCreate):
    form_class = DepositForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submenu'] = 'deposit'
        return context


class SplitCreate(LoginRequiredMixin, generic.edit.CreateView):
    model = Transaction
    template_name = 'silverstrike/newform.html'
    formset_class = TransactionFormSet
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(SplitCreate, self).get_context_data(**kwargs)
        context['formset'] = self.formset_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())

        if form.is_valid():
            transaction = form.save(commit=False)
            formset = self.formset_class(self.request.POST, instance=transaction)
            if formset.is_valid():
                transaction.save()
                formset.save()
                return HttpResponseRedirect('/')
        return self.render_to_response(self.get_context_data(form=form))


class SplitUpdate(LoginRequiredMixin, generic.edit.UpdateView):
    model = Transaction
    template_name = 'silverstrike/newform.html'
    formset_class = TransactionFormSet
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super(SplitUpdate, self).get_context_data(**kwargs)
        context['formset'] = self.formset_class(**self.get_form_kwargs())
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(self.get_form_class())

        if form.is_valid():
            transaction = form.save(commit=False)
            formset = self.formset_class(self.request.POST, instance=transaction)
            if formset.is_valid():
                fields = [form.cleaned_data.get('amount') for form in formset]
                split_sums = sum([x for x in fields if x is not None])
                if split_sums == 0:
                    transaction.save()
                    formset.save()
                    return HttpResponseRedirect('/')
                else:
                    form.add_error(
                        '',
                        'Sum of all splits has to be 0. You have {} remaining'.format(split_sums))
        return self.render_to_response(self.get_context_data(form=form))
