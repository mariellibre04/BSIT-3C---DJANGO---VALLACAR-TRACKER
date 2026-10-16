from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from apps.bus.models import Bus
from .models import Booking, active_holds


def _free_seats(bus):
    occupied = bus.passengers.count()
    return max(0, bus.capacity - occupied - active_holds(bus.id))


def _crew(bus):
    drivers = list(bus.drivers.all()) if hasattr(bus, 'drivers') else []
    conductors = list(bus.conductors.all()) if hasattr(bus, 'conductors') else []
    crew = []
    for d in drivers:
        crew.append({'role': 'Driver', 'name': d.name, 'contact': d.contact or '—'})
    for c in conductors:
        crew.append({'role': 'Conductor', 'name': c.name, 'contact': c.contact or '—'})
    return crew


@require_POST
def booking_create_ajax(request):
    """Public endpoint: a rider books seats on a bus with free seats.

    No login needed — this is what passengers use from their phones.
    """
    bus_id = request.POST.get('bus', '').strip()
    name = request.POST.get('passenger_name', '').strip()
    contact = request.POST.get('contact', '').strip()
    pickup = request.POST.get('pickup', '').strip()
    try:
        seats = int(request.POST.get('seats', '1') or 1)
    except ValueError:
        return JsonResponse({'error': 'Seats must be a number.'}, status=400)

    bus = Bus.objects.filter(pk=bus_id, status=Bus.STATUS_ACTIVE).first()
    if bus is None:
        return JsonResponse({'error': 'That bus is no longer available for booking.'}, status=400)
    if not name:
        return JsonResponse({'error': 'Your name is required.'}, status=400)
    if not contact:
        return JsonResponse({'error': 'A contact number is required so the crew can reach you.'}, status=400)
    if not pickup:
        return JsonResponse({'error': 'Please choose where you will board.'}, status=400)
    if seats < 1 or seats > 50:
        return JsonResponse({'error': 'You can book 1 to 50 seats.'}, status=400)
    free = _free_seats(bus)
    if seats > free:
        if free <= 0:
            return JsonResponse({'error': f'Bus "{bus.bus_number}" is already full.'}, status=400)
        return JsonResponse({'error': f'Only {free} seat(s) left on bus "{bus.bus_number}".'}, status=400)

    booking = Booking(bus=bus, passenger_name=name, contact=contact, pickup=pickup, seats=seats)
    try:
        booking.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save your booking. Please try again.'}, status=400)
    return JsonResponse({
        'status': 'booked',
        'reference': booking.reference,
        'bus_number': bus.bus_number,
        'seats': booking.seats,
        'pickup': booking.pickup,
        # Crew notified: driver / conductor assigned to this bus.
        'crew': _crew(bus),
    })


def _owned_booking(user, pk):
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Booking.objects.select_related('bus'), pk=pk, bus__user=user)


@login_required(login_url='login')
def booking_list_page(request):
    """Staff inbox: booking requests on your buses — confirm or decline.

    Confirming notifies the assigned driver / conductor to expect the rider.
    """
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    bookings = (Booking.objects.select_related('bus')
                .filter(bus__user=request.user).order_by('-created_at'))
    if query:
        bookings = bookings.filter(
            Q(passenger_name__icontains=query) | Q(contact__icontains=query)
            | Q(reference__icontains=query) | Q(pickup__icontains=query)
            | Q(bus__bus_number__icontains=query)
        )
    if status_filter in dict(Booking.STATUS_CHOICES):
        bookings = bookings.filter(status=status_filter)
    pending_count = Booking.objects.filter(bus__user=request.user, status=Booking.STATUS_PENDING).count()
    paginator = Paginator(bookings, 10)
    page = paginator.get_page(request.GET.get('page', 1))
    for bk in page.object_list:
        bk.crew = _crew(bk.bus)
    return render(request, 'bookings/list.html', {
        'bookings': page, 'query': query, 'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES, 'pending_count': pending_count,
    })


@login_required(login_url='login')
@require_POST
def booking_confirm_ajax(request, pk):
    booking = _owned_booking(request.user, pk)
    if booking.status != Booking.STATUS_PENDING:
        return JsonResponse({'error': 'Only pending bookings can be confirmed.'}, status=400)
    others_hold = (Booking.objects.filter(bus=booking.bus)
                   .exclude(pk=booking.pk)
                   .filter(status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]))
    from django.db.models import Sum
    others = others_hold.aggregate(v=Sum('seats'))['v'] or 0
    truly_free = max(0, booking.bus.capacity - booking.bus.passengers.count() - others)
    if booking.seats > truly_free:
        return JsonResponse(
            {'error': f'Not enough seats left on bus "{booking.bus.bus_number}" ({truly_free} free).'},
            status=400,
        )
    booking.status = Booking.STATUS_CONFIRMED
    booking.save(update_fields=['status', 'updated_at'])
    messages.success(request, f'Booking {booking.reference} confirmed — crew notified.')
    return JsonResponse({'status': 'confirmed', 'reference': booking.reference})


@login_required(login_url='login')
@require_POST
def booking_decline_ajax(request, pk):
    booking = _owned_booking(request.user, pk)
    if booking.status != Booking.STATUS_PENDING:
        return JsonResponse({'error': 'Only pending bookings can be declined.'}, status=400)
    booking.status = Booking.STATUS_DECLINED
    booking.save(update_fields=['status', 'updated_at'])
    messages.success(request, f'Booking {booking.reference} declined.')
    return JsonResponse({'status': 'declined'})


@login_required(login_url='login')
@require_POST
def booking_delete_ajax(request, pk):
    booking = _owned_booking(request.user, pk)
    ref = booking.reference
    booking.delete()
    messages.success(request, f'Booking {ref} deleted.')
    return JsonResponse({'status': 'deleted'})
