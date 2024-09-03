from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Service, AvailableSlot

def service_list(request):
    services = Service.objects.all()
    return render(request, 'service/service_list.html', {'services': services})

def available_slots(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    slots = AvailableSlot.objects.filter(service=service, is_booked=False)
    return render(request, 'service/available_slots.html', {'service': service, 'slots': slots})
