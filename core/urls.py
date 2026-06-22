from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/resident/', views.register_resident, name='register_resident'),
    path('register/provider/', views.register_provider, name='register_provider'),

    path('resident/dashboard/', views.resident_dashboard, name='resident_dashboard'),
    path('resident/reports/', views.resident_report_list, name='resident_report_list'),
    path('resident/reports/new/', views.resident_report_create, name='resident_report_create'),
    path('resident/reports/<int:report_id>/edit/', views.resident_report_edit, name='resident_report_edit'),
    path('resident/reports/<int:report_id>/delete/', views.resident_report_delete, name='resident_report_delete'),
    path('resident/schedule/', views.resident_schedule_view, name='resident_schedule'),
    path('resident/recycling-guide/', views.resident_recycling_guide, name='resident_recycling_guide'),

    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]