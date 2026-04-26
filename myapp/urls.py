from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_app, name='invoice_app'),
    path('admin-invoice-counter/', views.admin_invoice_counter, name='admin_invoice_counter'),
]