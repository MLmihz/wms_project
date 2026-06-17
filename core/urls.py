from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/resident/', views.register_resident, name='register_resident'),
    path('register/provider/', views.register_provider, name='register_provider'),

    path('resident/dashboard/', views.resident_dashboard, name='resident_dashboard'),
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]