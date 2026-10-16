from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list_page, name='booking_list'),
    # Public: passengers book from their phones without logging in.
    path('ajax/create/', views.booking_create_ajax, name='booking_create_ajax'),
    path('ajax/confirm/<int:pk>/', views.booking_confirm_ajax, name='booking_confirm_ajax'),
    path('ajax/decline/<int:pk>/', views.booking_decline_ajax, name='booking_decline_ajax'),
    path('ajax/delete/<int:pk>/', views.booking_delete_ajax, name='booking_delete_ajax'),
]
