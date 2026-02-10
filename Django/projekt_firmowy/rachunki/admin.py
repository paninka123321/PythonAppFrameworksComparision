from django.contrib import admin
from .models import Bill

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("year", "month", "category", "amount")
    list_filter = ("year", "category")
    ordering = ("year", "month")
