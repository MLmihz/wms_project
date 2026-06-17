from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Resident, WasteServiceProvider, Administrator


def get_user_role(user):
    """Return ('resident'|'provider'|'admin'|None, profile_object|None) for a logged-in User."""
    if hasattr(user, 'resident'):
        return 'resident', user.resident
    if hasattr(user, 'waste_service_provider'):
        return 'provider', user.waste_service_provider
    if hasattr(user, 'administrator'):
        return 'admin', user.administrator
    return None, None


def home_redirect(request):
    """Send a logged-in user to the right dashboard, or to login if anonymous."""
    if not request.user.is_authenticated:
        return redirect('login')

    role, _ = get_user_role(request.user)
    if role == 'resident':
        return redirect('resident_dashboard')
    if role == 'provider':
        return redirect('provider_dashboard')
    if role == 'admin':
        return redirect('admin_dashboard')

    # Logged in but no matching actor profile — safety fallback
    messages.error(request, "Your account has no assigned role. Contact an administrator.")
    logout(request)
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_resident(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number', '')
        address = request.POST.get('address', '')
        zone = request.POST.get('zone', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'auth/register_resident.html')

        user = User.objects.create_user(username=username, password=password)
        Resident.objects.create(
            user=user,
            full_name=full_name,
            phone_number=phone_number,
            address=address,
            zone=zone,
        )
        messages.success(request, "Registration successful. Please log in.")
        return redirect('login')

    return render(request, 'auth/register_resident.html')


def register_provider(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        company_name = request.POST.get('company_name')
        phone_number = request.POST.get('phone_number', '')
        coverage_zone = request.POST.get('coverage_zone', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'auth/register_provider.html')

        user = User.objects.create_user(username=username, password=password)
        WasteServiceProvider.objects.create(
            user=user,
            company_name=company_name,
            phone_number=phone_number,
            coverage_zone=coverage_zone,
        )
        messages.success(request, "Registration successful. Please log in.")
        return redirect('login')

    return render(request, 'auth/register_provider.html')


@login_required
def resident_dashboard(request):
    role, profile = get_user_role(request.user)
    if role != 'resident':
        return redirect('home')
    return render(request, 'resident/dashboard.html', {'resident': profile})


@login_required
def provider_dashboard(request):
    role, profile = get_user_role(request.user)
    if role != 'provider':
        return redirect('home')
    return render(request, 'provider/dashboard.html', {'provider': profile})


@login_required
def admin_dashboard(request):
    role, profile = get_user_role(request.user)
    if role != 'admin':
        return redirect('home')
    return render(request, 'admin/dashboard.html', {'admin': profile})