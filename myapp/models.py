from django.db import models
from django.db import transaction

class InvoiceCounter(models.Model):
    """Model to store the last used invoice number"""
    name = models.CharField(max_length=50, default='main', unique=True)
    last_invoice_number = models.IntegerField(default=12914)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Invoice Counter'
        verbose_name_plural = 'Invoice Counters'
    
    def __str__(self):
        return f"Invoice Counter: {self.last_invoice_number}"
    
    @classmethod
    def get_next_number(cls):
        """Get the next invoice number and increment"""
        with transaction.atomic():
            counter, created = cls.objects.select_for_update().get_or_create(
                name='main', 
                defaults={'last_invoice_number': 12914}
            )
            next_number = counter.last_invoice_number + 1
            counter.last_invoice_number = next_number
            counter.save()
            return next_number
    
    @classmethod
    def get_current_number(cls):
        """Get current invoice number without incrementing"""
        counter, created = cls.objects.get_or_create(
            name='main', 
            defaults={'last_invoice_number': 12914}
        )
        return counter.last_invoice_number
    
    @classmethod
    def set_number(cls, number):
        """Set specific invoice number (for admin/reset purposes)"""
        counter, created = cls.objects.get_or_create(
            name='main', 
            defaults={'last_invoice_number': 12914}
        )
        counter.last_invoice_number = number
        counter.save()
        return True