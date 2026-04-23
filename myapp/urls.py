from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_app, name='invoice_app'),
]