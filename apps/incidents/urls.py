from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    path('', views.incident_list_page, name='incident_list'),
    path('ajax/get/<int:pk>/', views.incident_get_ajax, name='incident_get_ajax'),
    path('ajax/save/', views.incident_save_ajax, name='incident_save_ajax'),
    path('ajax/resolve/<int:pk>/', views.incident_resolve_ajax, name='incident_resolve_ajax'),
    path('ajax/delete/<int:pk>/', views.incident_delete_ajax, name='incident_delete_ajax'),
]
