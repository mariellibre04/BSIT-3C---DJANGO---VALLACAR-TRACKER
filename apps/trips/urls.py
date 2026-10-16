from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.trip_list_page, name='trip_list'),
    path('alerts/', views.alerts_page, name='alerts'),
    path('reports/', views.reports_page, name='reports'),
    path('ajax/get/<int:pk>/', views.trip_get_ajax, name='trip_get_ajax'),
    path('ajax/save/', views.trip_save_ajax, name='trip_save_ajax'),
    path('ajax/delete/<int:pk>/', views.trip_delete_ajax, name='trip_delete_ajax'),
]
