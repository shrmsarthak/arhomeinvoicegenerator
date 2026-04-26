from django.contrib import admin
from .models import InvoiceCounter

@admin.register(InvoiceCounter)
class InvoiceCounterAdmin(admin.ModelAdmin):
    list_display = ['name', 'last_invoice_number', 'updated_at']
    readonly_fields = ['name', 'updated_at']
    fields = ['name', 'last_invoice_number', 'updated_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False