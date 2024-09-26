from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.manage_products, name='manage_products'),
    path('discounts/', views.manage_discounts, name='manage_discounts'),
    path('delivery/', views.manage_delivery, name='manage_delivery'),
    path('orders/', views.manage_orders, name='manage_orders'), 
]
