from django.db import models
from django.contrib.auth.models import User



# ACTOR TABLES


class Resident(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resident')
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    zone = models.CharField(max_length=100, blank=True)  # collection zone/area
    points = models.PositiveIntegerField(default=0)  # recycling reward points
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class WasteServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='waste_service_provider')
    company_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, blank=True)
    coverage_zone = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='administrator')
    full_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name



# WASTE REPORT 


class WasteReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('collected', 'Collected'),
        ('rejected', 'Rejected'),
    ]

    WASTE_TYPE_CHOICES = [
        ('organic', 'Organic'),
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('metal', 'Metal'),
        ('glass', 'Glass'),
        ('e_waste', 'E-Waste'),
        ('other', 'Other'),
    ]

    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='waste_reports')
    assigned_provider = models.ForeignKey(
        WasteServiceProvider, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_reports'
    )
    waste_type = models.CharField(max_length=20, choices=WASTE_TYPE_CHOICES)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_reported = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.waste_type} report at {self.location} ({self.status})"



# COLLECTION SCHEDULE 

class CollectionSchedule(models.Model):
    provider = models.ForeignKey(WasteServiceProvider, on_delete=models.CASCADE, related_name='schedules')
    zone = models.CharField(max_length=100)
    waste_type = models.CharField(max_length=20, choices=WasteReport.WASTE_TYPE_CHOICES)
    collection_date = models.DateField()
    collection_time = models.TimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.zone} - {self.collection_date} ({self.waste_type})"



# RECYCLING GUIDE (set by a WasteServiceProvider)


class RecyclingGuide(models.Model):
    provider = models.ForeignKey(WasteServiceProvider, on_delete=models.CASCADE, related_name='recycling_guides')
    waste_type = models.CharField(max_length=20, choices=WasteReport.WASTE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



# NOTIFICATION 


class Notification(models.Model):
    RECIPIENT_TYPE_CHOICES = [
        ('resident', 'Resident'),
        ('provider', 'Waste Service Provider'),
        ('admin', 'Administrator'),
    ]

    recipient_type = models.CharField(max_length=20, choices=RECIPIENT_TYPE_CHOICES)
    recipient_id = models.PositiveIntegerField()  # PK of Resident/Provider/Administrator
    message = models.CharField(max_length=255)
    waste_report = models.ForeignKey(
        WasteReport, on_delete=models.CASCADE,
        null=True, blank=True, related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient_type} #{self.recipient_id}: {self.message[:40]}"



# SYSTEM LOG 

class SystemLog(models.Model):
    ACTOR_TYPE_CHOICES = [
        ('resident', 'Resident'),
        ('provider', 'Waste Service Provider'),
        ('admin', 'Administrator'),
    ]

    actor_type = models.CharField(max_length=20, choices=ACTOR_TYPE_CHOICES)
    actor_id = models.PositiveIntegerField()
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor_type} #{self.actor_id}: {self.action}"
    