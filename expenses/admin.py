from django.contrib import admin
from .models import Expense, ExpenseSplit

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'paid_by', 'group', 'date']
    search_fields = ['description']
    list_filter = ['group']

@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ['expense', 'user', 'amount_owed', 'paid']
    list_filter = ['paid']
