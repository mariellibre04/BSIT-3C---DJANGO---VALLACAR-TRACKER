from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.maintenance_list_page, name='maintenance_list'),
    path('ajax/get/<int:pk>/', views.maintenance_get_ajax, name='maintenance_get_ajax'),
    path('ajax/save/', views.maintenance_save_ajax, name='maintenance_save_ajax'),
    path('ajax/delete/<int:pk>/', views.maintenance_delete_ajax, name='maintenance_delete_ajax'),
]
