from django.urls import path
from . import views

app_name = 'conductor'

urlpatterns = [
    path('', views.conductor_list_page, name='conductor_list'),
    path('ajax/list/', views.conductor_list_ajax, name='conductor_list_ajax'),
    path('ajax/get/<int:pk>/', views.conductor_get_ajax, name='conductor_get_ajax'),
    path('ajax/save/', views.conductor_save_ajax, name='conductor_save_ajax'),
    path('ajax/delete/<int:pk>/', views.conductor_delete_ajax, name='conductor_delete_ajax'),
]
