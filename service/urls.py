from django.urls import path
from . import views

app_name = 'service'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('<int:service_id>/slots/', views.available_slots, name='available_slots'),
]
