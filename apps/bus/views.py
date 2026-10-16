from decimal import Decimal, InvalidOperation

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone

from apps.scoping import scoped_bus, scoped_buses
from django.db.models import Count
from .models import Bus

MIN_CAPACITY = 1
MAX_CAPACITY = 100


def _parse_capacity(raw):
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _parse_coord(raw, low, high):
    raw = (raw or '').strip() if isinstance(raw, str) else raw
    if raw in (None, ''):
        return None, None
    try:
        value = Decimal(str(raw))
    except (InvalidOperation, ValueError, TypeError):
        return None, 'Enter a valid coordinate.'
    if value < low or value > high:
        return None, f'Coordinate out of range ({low} to {high}).'
    return value, None


def _bus_gps_payload(bus, occupied=None):
    if occupied is None:
        try:
            occupied = bus.total_passengers
        except AttributeError:
            occupied = bus.passengers.count()
    return {
        'id': bus.id,
        'bus_number': bus.bus_number,
        'plate_number': bus.plate_number,
        'capacity': bus.capacity,
        'route': bus.route,
        'status': bus.status,
        'current_location': bus.current_location or bus.route,
        'latitude': float(bus.latitude) if bus.latitude is not None else None,
        'longitude': float(bus.longitude) if bus.longitude is not None else None,
        'movement_status': bus.movement_status,
        'movement_display': bus.get_movement_status_display(),
        'last_gps_update': bus.last_gps_update.isoformat() if bus.last_gps_update else None,
        'passengers_count': occupied,
        'available_seats': max(0, bus.capacity - occupied),
        'is_full': max(0, bus.capacity - occupied) <= 0,
    }


@login_required(login_url='login')
def bus_list_page(request):
    query = request.GET.get('q', '').strip()
    buses_list = scoped_buses(request.user).annotate(
        total_passengers=Count('passengers')
    ).order_by('bus_number')
    if query:
        buses_list = buses_list.filter(
            Q(bus_number__icontains=query) |
            Q(plate_number__icontains=query) |
            Q(route__icontains=query) |
            Q(current_location__icontains=query)
        )
    paginator = Paginator(buses_list, 10)
    buses = paginator.get_page(request.GET.get('page', 1))
    for b in buses.object_list:
        b.seats_left = max(0, b.capacity - b.total_passengers)
    return render(request, 'bus/list.html', {'buses': buses, 'query': query})


@login_required(login_url='login')
def bus_list_ajax(request):
    query = request.GET.get('q', '').strip()
    buses_list = scoped_buses(request.user).annotate(
        total_passengers=Count('passengers')
    ).order_by('bus_number')
    if query:
        buses_list = buses_list.filter(
            Q(bus_number__icontains=query) |
            Q(plate_number__icontains=query) |
            Q(route__icontains=query) |
            Q(current_location__icontains=query)
        )
    paginator = Paginator(buses_list, 10)
    buses = paginator.get_page(request.GET.get('page', 1))
    data = []
    for b in buses.object_list:
        occupied = b.total_passengers
        data.append(_bus_gps_payload(b, occupied))
    return JsonResponse({
        'data': data,
        'has_next': buses.has_next(),
        'has_prev': buses.has_previous(),
        'page': buses.number,
        'pages': buses.paginator.num_pages,
        'total': buses.paginator.count,
    })


@login_required(login_url='login')
def bus_get_ajax(request, pk):
    bus = scoped_bus(request.user, pk)
    return JsonResponse(_bus_gps_payload(bus))


@login_required(login_url='login')
@require_POST
def bus_save_ajax(request):
    bus_id = request.POST.get('id')
    if bus_id:
        bus = scoped_bus(request.user, bus_id)
        is_update = True
    else:
        bus = Bus()
        is_update = False

    bus_number = request.POST.get('bus_number', '').strip()
    plate_number = request.POST.get('plate_number', '').strip()
    capacity = request.POST.get('capacity', '').strip()
    route = request.POST.get('route', '').strip()
    status = request.POST.get('status', Bus.STATUS_ACTIVE).strip()
    current_location = request.POST.get('current_location', '').strip()
    movement_status = request.POST.get('movement_status', Bus.MOVE_AT_TERMINAL).strip()
    latitude, lat_error = _parse_coord(request.POST.get('latitude', ''), Decimal('-90'), Decimal('90'))
    longitude, lng_error = _parse_coord(request.POST.get('longitude', ''), Decimal('-180'), Decimal('180'))

    if not bus_number:
        return JsonResponse({'error': 'Bus number is required.'}, status=400)
    if not plate_number:
        return JsonResponse({'error': 'Plate number is required.'}, status=400)
    if not capacity:
        return JsonResponse({'error': 'Capacity is required.'}, status=400)
    capacity_value = _parse_capacity(capacity)
    if capacity_value is None or capacity_value < MIN_CAPACITY or capacity_value > MAX_CAPACITY:
        return JsonResponse(
            {'error': f'Capacity must be a number between {MIN_CAPACITY} and {MAX_CAPACITY}.'},
            status=400,
        )
    if not route:
        return JsonResponse({'error': 'Route is required.'}, status=400)
    if status not in dict(Bus.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status.'}, status=400)
    if movement_status not in dict(Bus.MOVEMENT_CHOICES):
        return JsonResponse({'error': 'Invalid movement status.'}, status=400)
    if lat_error:
        return JsonResponse({'error': f'Latitude: {lat_error}'}, status=400)
    if lng_error:
        return JsonResponse({'error': f'Longitude: {lng_error}'}, status=400)
    if (latitude is None) != (longitude is None):
        return JsonResponse({'error': 'Latitude and longitude must be set together.'}, status=400)

    dup = Bus.objects.filter(Q(bus_number=bus_number) | Q(plate_number=plate_number))
    if bus_id:
        dup = dup.exclude(pk=bus_id)
    if dup.filter(bus_number=bus_number).exists():
        return JsonResponse({'error': 'That bus number already exists.'}, status=400)
    if dup.filter(plate_number=plate_number).exists():
        return JsonResponse({'error': 'That plate number already exists.'}, status=400)

    if bus_id:
        occupied = bus.passengers.count()
        if capacity_value < occupied:
            return JsonResponse(
                {'error': f'Capacity cannot be less than assigned passengers ({occupied}).'},
                status=400,
            )

    gps_changed = (
        (bus.pk is None and (current_location or latitude is not None))
        or (bus.pk and (
            bus.current_location != current_location
            or bus.movement_status != movement_status
            or (str(bus.latitude) if bus.latitude is not None else None) != (str(latitude) if latitude is not None else None)
            or (str(bus.longitude) if bus.longitude is not None else None) != (str(longitude) if longitude is not None else None)
        ))
    )
    bus.bus_number = bus_number
    bus.plate_number = plate_number
    bus.capacity = capacity_value
    bus.route = route
    bus.status = status
    bus.current_location = current_location
    bus.latitude = latitude
    bus.longitude = longitude
    bus.movement_status = movement_status
    if gps_changed:
        bus.last_gps_update = timezone.now()
    if not bus.pk:
        bus.user = request.user

    try:
        bus.save()
    except IntegrityError:
        return JsonResponse({'error': 'Could not save bus due to a conflict.'}, status=400)

    messages.success(
        request,
        f'Bus "{bus.bus_number}" has been {"updated" if is_update else "saved"} successfully.'
    )
    payload = _bus_gps_payload(bus)
    payload['status'] = 'success'
    return JsonResponse(payload)


@login_required(login_url='login')
@require_POST
def bus_delete_ajax(request, pk):
    bus = scoped_bus(request.user, pk)
    name = bus.bus_number
    bus.delete()
    messages.success(request, f'Bus "{name}" has been deleted successfully.')
    return JsonResponse({'status': 'deleted'})


@login_required(login_url='login')
def bus_map_page(request):
    """1. Real-Time GPS Tracking map: current location of each bus + route + movement."""
    buses = list(scoped_buses(request.user).annotate(total_passengers=Count('passengers')).order_by('bus_number'))
    for b in buses:
        b.seats_left = max(0, b.capacity - (b.total_passengers or 0))
    with_gps = sum(1 for b in buses if b.latitude is not None and b.longitude is not None)
    return render(request, 'bus/map.html', {
        'buses': buses, 'with_gps': with_gps,
        'movement_choices': Bus.MOVEMENT_CHOICES,
        # Vallacar / Bacolod default center when a bus has no GPS fix yet
        'default_lat': 10.6765, 'default_lng': 122.9509,
    })


@login_required(login_url='login')
def bus_locations_ajax(request):
    """JSON feed for the live map: location, route, movement, seats."""
    buses = scoped_buses(request.user).annotate(total_passengers=Count('passengers')).order_by('bus_number')
    return JsonResponse({'buses': [_bus_gps_payload(b, b.total_passengers) for b in buses]})


@login_required(login_url='login')
@require_POST
def bus_gps_update_ajax(request, pk):
    """Quick GPS ping: update location / coordinates / movement from the map."""
    bus = scoped_bus(request.user, pk)
    current_location = request.POST.get('current_location', '').strip()
    movement_status = request.POST.get('movement_status', '').strip() or bus.movement_status
    latitude, lat_error = _parse_coord(request.POST.get('latitude', ''), Decimal('-90'), Decimal('90'))
    longitude, lng_error = _parse_coord(request.POST.get('longitude', ''), Decimal('-180'), Decimal('180'))
    if movement_status not in dict(Bus.MOVEMENT_CHOICES):
        return JsonResponse({'error': 'Invalid movement status.'}, status=400)
    if lat_error:
        return JsonResponse({'error': f'Latitude: {lat_error}'}, status=400)
    if lng_error:
        return JsonResponse({'error': f'Longitude: {lng_error}'}, status=400)
    if (latitude is None) != (longitude is None):
        return JsonResponse({'error': 'Latitude and longitude must be set together.'}, status=400)
    if current_location:
        bus.current_location = current_location
    if latitude is not None:
        bus.latitude = latitude
        bus.longitude = longitude
    bus.movement_status = movement_status
    bus.last_gps_update = timezone.now()
    bus.save(update_fields=['current_location', 'latitude', 'longitude', 'movement_status', 'last_gps_update', 'updated_at'])
    messages.success(request, f'GPS for bus "{bus.bus_number}" updated.')
    payload = _bus_gps_payload(bus)
    payload['status'] = 'updated'
    return JsonResponse(payload)
