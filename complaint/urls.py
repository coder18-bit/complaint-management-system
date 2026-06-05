from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    # Admin
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/complaint/new/', views.admin_register_complaint, name='admin_register_complaint'),
    path('admin-panel/complaint/<int:pk>/', views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin-panel/engineers/', views.engineer_list, name='engineer_list'),
    path('admin-panel/engineers/add/', views.add_engineer, name='add_engineer'),
    path(
    'admin-panel/complaint/<int:pk>/update/',
    views.admin_update_complaint,
    name='admin_update_complaint'
),

    # Engineer
    path('engineer/', views.engineer_dashboard, name='engineer_dashboard'),
    path('engineer/complaint/new/', views.engineer_register_complaint, name='engineer_register_complaint'),
    path('engineer/complaint/<int:pk>/', views.engineer_complaint_detail, name='engineer_complaint_detail'),
    path(
    'admin-panel/engineers/edit/<int:pk>/',
    views.edit_engineer,
    name='edit_engineer'
),
]