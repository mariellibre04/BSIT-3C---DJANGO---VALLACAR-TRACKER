from django.urls import path
from . import views

app_name = 'passengers'

urlpatterns = [
    path('', views.passenger_list_page, name='passenger_list'),
    path('ajax/list/', views.passenger_list_ajax, name='passenger_list_ajax'),
    path('ajax/get/<int:pk>/', views.passenger_get_ajax, name='passenger_get_ajax'),
    path('ajax/save/', views.passenger_save_ajax, name='passenger_save_ajax'),
    path('ajax/delete/<int:pk>/', views.passenger_delete_ajax, name='passenger_delete_ajax'),
]
