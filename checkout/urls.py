from django.urls import path
from . import views
from checkout.webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('update-delivery/<int:delivery_id>/', views.update_delivery, name='update_delivery'),
    path('checkout_success/<str:order_number>/', views.checkout_success, name='checkout_success'),
    path('wh/', webhook, name='webhook'),
]
