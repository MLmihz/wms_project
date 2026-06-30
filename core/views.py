from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from .models import (
    SystemLog,
    Resident,
    WasteServiceProvider,
    Administrator,
    WasteReport,
    CollectionSchedule,
    RecyclingGuide,
    Notification,
)
from .forms import WasteReportForm


def get_user_role(user):
    if hasattr(user, 'administrator'):
        return 'admin', user.administrator
    if hasattr(user, 'waste_service_provider'):
        return 'provider', user.waste_service_provider
    if hasattr(user, 'resident'):
        return 'resident', user.resident
    return None, None


def _require_role(request, expected_role):
    role, profile = get_user_role(request.user)
    if role != expected_role:
        messages.error(request, "You do not have permission to access this page.")
        return None
    if hasattr(profile, 'is_active') and not profile.is_active:
        messages.error(request, "Your account is deactivated. Contact an administrator.")
        logout(request)
        return None
    return profile


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
            role, profile = get_user_role(user)

            if profile is not None and hasattr(profile, 'is_active') and not profile.is_active:
                messages.error(request, "This account has been deactivated. Contact an administrator.")
                return render(request, 'auth/login.html')

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
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        zone = request.POST.get('zone', '').strip()

        form_errors = {}

        if User.objects.filter(username=username).exists():
            form_errors['username'] = "Username already taken. Please choose a different one."

        if len(password) < 8:
            form_errors['password'] = "Password must be at least 8 characters long."

        if password != confirm_password:
            form_errors['confirm_password'] = "Passwords do not match."

        if phone_number and (not phone_number.isdigit() or len(phone_number) != 10):
            form_errors['phone_number'] = "Phone number must be exactly 10 digits."

        if form_errors:
            messages.error(request, "Please correct the highlighted errors and try again.")
            return render(request, 'auth/register_resident.html', {
                'form_errors': form_errors,
                'form_data': {
                    'username': username,
                    'full_name': full_name,
                    'phone_number': phone_number,
                    'address': address,
                    'zone': zone,
                },
            })

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
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        company_name = request.POST.get('company_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        coverage_zone = request.POST.get('coverage_zone', '').strip()

        form_errors = {}

        if User.objects.filter(username=username).exists():
            form_errors['username'] = "Username already taken. Please choose a different one."

        if len(password) < 8:
            form_errors['password'] = "Password must be at least 8 characters long."

        if password != confirm_password:
            form_errors['confirm_password'] = "Passwords do not match."

        if phone_number and (not phone_number.isdigit() or len(phone_number) != 10):
            form_errors['phone_number'] = "Phone number must be exactly 10 digits."

        if form_errors:
            messages.error(request, "Please correct the highlighted errors and try again.")
            return render(request, 'provider/register.html', {
                'form_errors': form_errors,
                'form_data': {
                    'company_name': company_name,
                    'username': username,
                    'phone_number': phone_number,
                    'coverage_zone': coverage_zone,
                },
            })

        user = User.objects.create_user(username=username, password=password)
        WasteServiceProvider.objects.create(
            user=user,
            company_name=company_name,
            phone_number=phone_number,
            coverage_zone=coverage_zone,
        )
        messages.success(request, "Registration successful. Please log in.")
        return redirect('login')

    return render(request, 'provider/register.html')


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
    profile = _require_role(request, 'provider')
    if profile is None:
        return redirect('home')

    my_reports = WasteReport.objects.filter(assigned_provider=profile).count()
    unassigned_reports = WasteReport.objects.filter(assigned_provider__isnull=True).count()
    pending_my_reports = WasteReport.objects.filter(assigned_provider=profile, status='pending').count()
    collected_my_reports = WasteReport.objects.filter(assigned_provider=profile, status='collected').count()
    schedules_count = CollectionSchedule.objects.filter(provider=profile).count()
    guides_count = RecyclingGuide.objects.filter(provider=profile).count()

    now = timezone.localtime()
    zone_status = []
    zones = (
        CollectionSchedule.objects
        .filter(provider=profile)
        .values_list('zone', flat=True)
        .distinct()
    )
    for zone in zones:
        latest_schedule = (
            CollectionSchedule.objects
            .filter(provider=profile, zone=zone)
            .order_by('-collection_date', '-collection_time')
            .first()
        )
        if latest_schedule is None:
            continue

        scheduled_at = timezone.make_aware(
            timezone.datetime.combine(
                latest_schedule.collection_date,
                latest_schedule.collection_time,
            )
        )
        zone_status.append({
            'zone': zone,
            'scheduled_at': scheduled_at,
            'is_done': scheduled_at <= now,
        })

    zone_status.sort(key=lambda row: row['zone'].lower())

    residents_for_points = Resident.objects.filter(is_active=True).order_by('full_name')
    if profile.coverage_zone:
        residents_for_points = residents_for_points.filter(zone__iexact=profile.coverage_zone)

    return render(request, 'provider/dashboard.html', {
        'provider': profile,
        'my_reports': my_reports,
        'unassigned_reports': unassigned_reports,
        'pending_my_reports': pending_my_reports,
        'collected_my_reports': collected_my_reports,
        'schedules_count': schedules_count,
        'guides_count': guides_count,
        'zone_status': zone_status,
        'residents_for_points': residents_for_points,
        'waste_type_choices': WasteReport.WASTE_TYPE_CHOICES,
    })


@login_required
def admin_dashboard(request):
    profile = _require_role(request, 'admin')
    if profile is None:
        return redirect('home')

    context = {
        'admin': profile,
        'total_residents': Resident.objects.count(),
        'active_residents': Resident.objects.filter(is_active=True).count(),
        'total_providers': WasteServiceProvider.objects.count(),
        'active_providers': WasteServiceProvider.objects.filter(is_active=True).count(),
        'pending_reports': WasteReport.objects.filter(status='pending').count(),
        'in_progress_reports': WasteReport.objects.filter(status='in_progress').count(),
        'collected_reports': WasteReport.objects.filter(status='collected').count(),
        'recent_logs': SystemLog.objects.order_by('-timestamp')[:10],
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
def create_admin(request):
    profile = _require_role(request, 'admin')
    if profile is None:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        full_name = request.POST.get('full_name')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'admin/create_admin.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'admin/create_admin.html')

        new_user = User.objects.create_user(username=username, password=password)
        Administrator.objects.create(user=new_user, full_name=full_name)

        SystemLog.objects.create(
            actor_type='admin',
            actor_id=profile.id,
            action=f"created admin account: {username}",
        )

        messages.success(request, f"Admin account '{username}' created successfully.")
        return redirect('admin_dashboard')

    return render(request, 'admin/create_admin.html')


@login_required
def manage_accounts(request):
    profile = _require_role(request, 'admin')
    if profile is None:
        return redirect('home')

    residents = Resident.objects.all()
    providers = WasteServiceProvider.objects.all()
    admins = Administrator.objects.all()

    return render(request, 'admin/manage_accounts.html', {
        'admin': profile,
        'residents': residents,
        'providers': providers,
        'admins': admins,
    })


@login_required
def toggle_resident_status(request, resident_id):
    admin_profile = _require_role(request, 'admin')
    if admin_profile is None:
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('manage_accounts')

    resident = get_object_or_404(Resident, id=resident_id)
    resident.is_active = not resident.is_active
    resident.save()

    action = "activated" if resident.is_active else "deactivated"
    SystemLog.objects.create(
        actor_type='admin',
        actor_id=admin_profile.id,
        action=f"{action} resident account: {resident.full_name}",
    )

    messages.success(request, f"{resident.full_name} has been {action}.")
    return redirect('manage_accounts')


@login_required
def toggle_provider_status(request, provider_id):
    admin_profile = _require_role(request, 'admin')
    if admin_profile is None:
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('manage_accounts')

    provider = get_object_or_404(WasteServiceProvider, id=provider_id)
    provider.is_active = not provider.is_active
    provider.save()

    action = "activated" if provider.is_active else "deactivated"
    SystemLog.objects.create(
        actor_type='admin',
        actor_id=admin_profile.id,
        action=f"{action} provider account: {provider.company_name}",
    )

    messages.success(request, f"{provider.company_name} has been {action}.")
    return redirect('manage_accounts')


@login_required
def view_waste_reports(request):
    provider_profile = _require_role(request, 'provider')
    if provider_profile is None:
        return redirect('home')

    unassigned_reports = WasteReport.objects.filter(assigned_provider__isnull=True).order_by('-date_reported')
    my_reports = WasteReport.objects.filter(assigned_provider=provider_profile).order_by('-date_reported')

    return render(request, 'provider/waste_reports.html', {
        'unassigned_reports': unassigned_reports,
        'my_reports': my_reports,
        'status_choices': WasteReport.STATUS_CHOICES,
    })


@login_required
def claim_report(request, report_id):
    provider_profile = _require_role(request, 'provider')
    if provider_profile is None:
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('view_waste_reports')

    report = get_object_or_404(WasteReport, id=report_id)
    if report.assigned_provider and report.assigned_provider != provider_profile:
        messages.error(request, "This report has already been claimed by another provider.")
        return redirect('view_waste_reports')

    report.assigned_provider = provider_profile
    report.status = 'in_progress'
    report.save()

    Notification.objects.create(
        recipient_type='resident',
        recipient_id=report.resident.id,
        message=f"Your waste report at {report.location} has been picked up by {provider_profile.company_name}.",
        waste_report=report,
    )

    SystemLog.objects.create(
        actor_type='provider',
        actor_id=provider_profile.id,
        action=f"claimed waste report #{report.id} at {report.location}",
    )

    messages.success(request, "Report claimed and marked in progress.")
    return redirect('view_waste_reports')


@login_required
def update_report_status(request, report_id):
    provider_profile = _require_role(request, 'provider')
    if provider_profile is None:
        return redirect('home')

    report = get_object_or_404(WasteReport, id=report_id, assigned_provider=provider_profile)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in dict(WasteReport.STATUS_CHOICES):
            report.status = new_status
            if new_status == 'collected':
                report.date_resolved = timezone.now()
            else:
                report.date_resolved = None
            report.save()

            Notification.objects.create(
                recipient_type='resident',
                recipient_id=report.resident.id,
                message=(
                    f"Your waste report at {report.location} is now: "
                    f"{report.get_status_display()}."
                ),
                waste_report=report,
            )

            SystemLog.objects.create(
                actor_type='provider',
                actor_id=provider_profile.id,
                action=f"updated waste report #{report.id} to status '{new_status}'",
            )

            messages.success(request, "Report status updated.")

    return redirect('view_waste_reports')


@login_required
def assign_collection_points(request):
    provider_profile = _require_role(request, 'provider')
    if provider_profile is None:
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('provider_dashboard')

    resident_id = request.POST.get('resident_id')
    waste_type = request.POST.get('waste_type', '').strip()
    quantity_kg = request.POST.get('quantity_kg', '').strip()

    resident = get_object_or_404(Resident, id=resident_id, is_active=True)

    if provider_profile.coverage_zone and resident.zone and resident.zone.lower() != provider_profile.coverage_zone.lower():
        messages.error(request, "You can only assign collection points to residents in your coverage zone.")
        return redirect('provider_dashboard')

    points_raw = request.POST.get('points', '0').strip()
    try:
        points = int(points_raw or '0')
        if points <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Please enter a valid positive points value.")
        return redirect('provider_dashboard')

    resident.points += points
    resident.save(update_fields=['points'])

    collection_note = ""
    if waste_type:
        collection_note = f" for {waste_type.replace('_', ' ')}"
    if quantity_kg:
        collection_note += f" ({quantity_kg} kg)"

    Notification.objects.create(
        recipient_type='resident',
        recipient_id=resident.id,
        message=f"You have been awarded {points} points for recycled collection{collection_note}.",
    )

    SystemLog.objects.create(
        actor_type='provider',
        actor_id=provider_profile.id,
        action=f"awarded {points} collection points to resident #{resident.id}{collection_note}",
    )

    messages.success(request, f"Awarded {points} collection points to {resident.full_name}.")
    return redirect('provider_dashboard')


@login_required
def manage_schedules(request):
    provider_profile = _require_role(request, 'provider')
    if provider_profile is None:
        return redirect('home')

    waste_type_choices = WasteReport.WASTE_TYPE_CHOICES
    valid_waste_types = {value for value, _ in waste_type_choices}

    edit_schedule = None
    edit_id = request.GET.get('edit')
    if edit_id:
        edit_schedule = get_object_or_404(CollectionSchedule, id=edit_id, provider=provider_profile)

    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        zone = request.POST.get('zone')
        waste_type = request.POST.get('waste_type')
        collection_date = request.POST.get('collection_date')
        collection_time = request.POST.get('collection_time')
        notes = request.POST.get('notes', '')

        if waste_type not in valid_waste_types:
            messages.error(request, "Invalid waste type selected.")
            return redirect('manage_schedules')

        if schedule_id:
            schedule = get_object_or_404(CollectionSchedule, id=schedule_id, provider=provider_profile)
            schedule.zone = zone
            schedule.waste_type = waste_type
            schedule.collection_date = collection_date
            schedule.collection_time = collection_time
            schedule.notes = notes
            schedule.save()

            SystemLog.objects.create(
                actor_type='provider',
                actor_id=provider_profile.id,
                action=f"updated collection schedule #{schedule.id} for {zone} on {collection_date}",
            )
            messages.success(request, "Collection schedule updated.")
            return redirect('manage_schedules')

        CollectionSchedule.objects.create(
            provider=provider_profile,
            zone=zone,
            waste_type=waste_type,
            collection_date=collection_date,
            collection_time=collection_time,
            notes=notes,
        )

        SystemLog.objects.create(
            actor_type='provider',
            actor_id=provider_profile.id,
            action=f"created collection schedule for {zone} on {collection_date}",
        )

        messages.success(request, "Collection schedule created.")
        return redirect('manage_schedules')

    schedules = CollectionSchedule.objects.filter(provider=provider_profile).order_by('-collection_date')

    return render(request, 'provider/manage_schedules.html', {
        'schedules': schedules,
        'waste_type_choices': waste_type_choices,
        'edit_schedule': edit_schedule,
    })


@login_required
def delete_schedule(request, schedule_id):
    provider_profile = _require_role(request, 'provider')
    if provider_profile is None:
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('manage_schedules')

    schedule = get_object_or_404(CollectionSchedule, id=schedule_id, provider=provider_profile)
    schedule.delete()
    messages.success(request, "Schedule deleted.")
    return redirect('manage_schedules')


@login_required
def manage_recycling_guides(request):
    provider_profile = _require_role(request, 'provider')
    if provider_profile is None:
        return redirect('home')

    if request.method == 'POST':
        waste_type = request.POST.get('waste_type')
        title = request.POST.get('title')
        instructions = request.POST.get('instructions')

        RecyclingGuide.objects.create(
            provider=provider_profile,
            waste_type=waste_type,
            title=title,
            instructions=instructions,
        )

        SystemLog.objects.create(
            actor_type='provider',
            actor_id=provider_profile.id,
            action=f"created recycling guide: {title}",
        )

        messages.success(request, "Recycling guide created.")
        return redirect('manage_recycling_guides')

    guides = RecyclingGuide.objects.filter(provider=provider_profile).order_by('-created_at')
    waste_type_choices = WasteReport.WASTE_TYPE_CHOICES

    return render(request, 'provider/manage_recycling_guides.html', {
        'guides': guides,
        'waste_type_choices': waste_type_choices,
    })


@login_required
def delete_recycling_guide(request, guide_id):
    provider_profile = _require_role(request, 'provider')
    if provider_profile is None:
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('home')

    guide = get_object_or_404(RecyclingGuide, id=guide_id, provider=provider_profile)
    guide.delete()
    messages.success(request, "Recycling guide deleted.")
    return redirect('manage_recycling_guides')


@login_required
def view_system_logs(request):
    admin_profile = _require_role(request, 'admin')
    if admin_profile is None:
        return redirect('home')

    actor_type = request.GET.get('actor_type', '')
    logs = SystemLog.objects.all().order_by('-timestamp')
    if actor_type in {'resident', 'provider', 'admin'}:
        logs = logs.filter(actor_type=actor_type)

    return render(request, 'admin/system_logs.html', {
        'logs': logs[:300],
        'actor_type': actor_type,
    })


@login_required
def generate_system_reports(request):
    admin_profile = _require_role(request, 'admin')
    if admin_profile is None:
        return redirect('home')

    days = request.GET.get('days', '30')
    try:
        days = int(days)
    except ValueError:
        days = 30

    if days <= 0:
        days = 30

    since = timezone.now() - timezone.timedelta(days=days)
    report_qs = WasteReport.objects.filter(date_reported__gte=since)

    status_breakdown = report_qs.values('status').annotate(total=Count('id')).order_by('status')
    waste_type_breakdown = report_qs.values('waste_type').annotate(total=Count('id')).order_by('waste_type')

    context = {
        'days': days,
        'since': since,
        'total_reports': report_qs.count(),
        'pending_reports': report_qs.filter(status='pending').count(),
        'in_progress_reports': report_qs.filter(status='in_progress').count(),
        'collected_reports': report_qs.filter(status='collected').count(),
        'rejected_reports': report_qs.filter(status='rejected').count(),
        'new_residents': Resident.objects.filter(date_joined__gte=since).count(),
        'new_providers': WasteServiceProvider.objects.filter(date_joined__gte=since).count(),
        'status_breakdown': status_breakdown,
        'waste_type_breakdown': waste_type_breakdown,
    }
    return render(request, 'admin/system_reports.html', context)


@login_required
def send_system_notification(request):
    admin_profile = _require_role(request, 'admin')
    if admin_profile is None:
        return redirect('home')

    if request.method == 'POST':
        audience = request.POST.get('audience', 'all')
        message = request.POST.get('message', '').strip()

        if not message:
            messages.error(request, "Notification message is required.")
            return redirect('send_system_notification')

        notification_batch = []
        recipients_count = 0

        if audience in {'all', 'residents'}:
            residents = Resident.objects.filter(is_active=True)
            notification_batch.extend([
                Notification(
                    recipient_type='resident',
                    recipient_id=resident.id,
                    message=message,
                )
                for resident in residents
            ])
            recipients_count += residents.count()

        if audience in {'all', 'providers'}:
            providers = WasteServiceProvider.objects.filter(is_active=True)
            notification_batch.extend([
                Notification(
                    recipient_type='provider',
                    recipient_id=provider.id,
                    message=message,
                )
                for provider in providers
            ])
            recipients_count += providers.count()

        if audience in {'all', 'admins'}:
            admins = Administrator.objects.filter(is_active=True)
            notification_batch.extend([
                Notification(
                    recipient_type='admin',
                    recipient_id=admin.id,
                    message=message,
                )
                for admin in admins
            ])
            recipients_count += admins.count()

        Notification.objects.bulk_create(notification_batch)

        SystemLog.objects.create(
            actor_type='admin',
            actor_id=admin_profile.id,
            action=f"sent system notification to {recipients_count} recipients ({audience})",
        )

        messages.success(request, f"Notification sent to {recipients_count} recipients.")
        return redirect('send_system_notification')

    return render(request, 'admin/send_notifications.html')