from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index_two/', views.index_two, name='index_two'),
]