from ..models import InvoiceCounter

def get_next_invoice_number():
    """Get the next invoice number and increment"""
    return InvoiceCounter.get_next_number()

def get_current_invoice_number():
    """Get current invoice number without incrementing"""
    return InvoiceCounter.get_current_number()

def set_invoice_number(number):
    """Set specific invoice number (for admin/reset purposes)"""
    return InvoiceCounter.set_number(number)

def reset_invoice_number(number=12914):
    """Reset invoice number to specified value"""
    return InvoiceCounter.set_number(number)