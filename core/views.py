from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import (
    Resident, WasteServiceProvider, Administrator,
    WasteReport, CollectionSchedule, RecyclingGuide,
)
from .forms import WasteReportForm


def get_user_role(user):
    if hasattr(user, 'resident'):
        return 'resident', user.resident
    if hasattr(user, 'waste_service_provider'):
        return 'provider', user.waste_service_provider
    if hasattr(user, 'administrator'):
        return 'admin', user.administrator
    return None, None


def home_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')

    role, _ = get_user_role(request.user)
    if role == 'resident':
        return redirect('resident_dashboard')
    if role == 'provider':
        return redirect('provider_dashboard')
    if role == 'admin':
        return redirect('admin_dashboard')

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

    recent_reports = profile.waste_reports.order_by('-date_reported')[:5]
    return render(request, 'resident/dashboard.html', {
        'resident': profile,
        'recent_reports': recent_reports,
    })


@login_required
def resident_report_list(request):
    role, profile = get_user_role(request.user)
    if role != 'resident':
        return redirect('home')

    reports = profile.waste_reports.order_by('-date_reported')
    return render(request, 'resident/report_list.html', {
        'resident': profile,
        'reports': reports,
    })


@login_required
def resident_report_create(request):
    role, profile = get_user_role(request.user)
    if role != 'resident':
        return redirect('home')

    if request.method == 'POST':
        form = WasteReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.resident = profile
            report.save()
            messages.success(request, "Your report has been submitted.")
            return redirect('resident_report_list')
    else:
        form = WasteReportForm()

    return render(request, 'resident/report_form.html', {
        'form': form,
        'editing': False,
    })


@login_required
def resident_report_edit(request, report_id):
    role, profile = get_user_role(request.user)
    if role != 'resident':
        return redirect('home')

    report = get_object_or_404(WasteReport, id=report_id, resident=profile)

    if report.status != 'pending':
        messages.error(request, "This report can no longer be edited because it is already being processed.")
        return redirect('resident_report_list')

    if request.method == 'POST':
        form = WasteReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, "Report updated.")
            return redirect('resident_report_list')
    else:
        form = WasteReportForm(instance=report)

    return render(request, 'resident/report_form.html', {
        'form': form,
        'editing': True,
        'report': report,
    })


@login_required
def resident_report_delete(request, report_id):
    role, profile = get_user_role(request.user)
    if role != 'resident':
        return redirect('home')

    report = get_object_or_404(WasteReport, id=report_id, resident=profile)

    if report.status != 'pending':
        messages.error(request, "This report can no longer be deleted because it is already being processed.")
        return redirect('resident_report_list')

    if request.method == 'POST':
        report.delete()
        messages.success(request, "Report deleted.")
        return redirect('resident_report_list')

    return render(request, 'resident/report_confirm_delete.html', {'report': report})


@login_required
def resident_schedule_view(request):
    role, profile = get_user_role(request.user)
    if role != 'resident':
        return redirect('home')

    schedules = CollectionSchedule.objects.order_by('collection_date', 'collection_time')
    return render(request, 'resident/schedule.html', {
        'resident': profile,
        'schedules': schedules,
    })


@login_required
def resident_recycling_guide(request):
    role, profile = get_user_role(request.user)
    if role != 'resident':
        return redirect('home')

    guides = RecyclingGuide.objects.order_by('waste_type')
    waste_type_filter = request.GET.get('waste_type')
    if waste_type_filter:
        guides = guides.filter(waste_type=waste_type_filter)

    return render(request, 'resident/recycling_guide.html', {
        'resident': profile,
        'guides': guides,
        'waste_type_choices': WasteReport.WASTE_TYPE_CHOICES,
        'selected_type': waste_type_filter,
    })


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