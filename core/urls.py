from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
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
    path('admin-panel/create-admin/', views.create_admin, name='create_admin'),
    path('admin-panel/manage-accounts/', views.manage_accounts, name='manage_accounts'),
    path('admin-panel/logs/', views.view_system_logs, name='view_system_logs'),
    path('admin-panel/reports/', views.generate_system_reports, name='generate_system_reports'),
    path('admin-panel/notifications/', views.send_system_notification, name='send_system_notification'),
    path('admin-panel/toggle-resident/<int:resident_id>/', views.toggle_resident_status, name='toggle_resident_status'),
    path('admin-panel/toggle-provider/<int:provider_id>/', views.toggle_provider_status, name='toggle_provider_status'),
    path('provider/reports/', views.view_waste_reports, name='view_waste_reports'),
    path('provider/reports/<int:report_id>/claim/', views.claim_report, name='claim_report'),
    path('provider/reports/<int:report_id>/update/', views.update_report_status, name='update_report_status'),
    path('provider/collection-points/assign/', views.assign_collection_points, name='assign_collection_points'),
    path('provider/schedules/', views.manage_schedules, name='manage_schedules'),
    path('provider/schedules/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('provider/recycling-guides/', views.manage_recycling_guides, name='manage_recycling_guides'),
    path('provider/recycling-guides/<int:guide_id>/delete/', views.delete_recycling_guide, name='delete_recycling_guide'),
]