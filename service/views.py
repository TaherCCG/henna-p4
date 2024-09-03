from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Service, AvailableSlot

def service_list(request):
    services = Service.objects.all()
    return render(request, 'service/service_list.html', {'services': services})

def available_slots(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    slots = AvailableSlot.objects.filter(service=service, is_booked=False)
    return render(request, 'service/available_slots.html', {'service': service, 'slots': slots})

def get_slots(request, service_id):
    date = request.GET.get('date')
    service = get_object_or_404(Service, id=service_id)
    slots = AvailableSlot.objects.filter(service=service, date=date, is_booked=False)
    slots_data = [{
        'time': slot.time.strftime('%H:%M'),
        'book_url': reverse('service:book_slot', args=[slot.id])
    } for slot in slots]
    return JsonResponse({'slots': slots_data})

def book_slot(request, slot_id):
    # Will Implement the booking logic here
    pass