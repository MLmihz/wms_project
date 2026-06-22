from django.contrib import admin
from .models import (
    Resident,
    WasteServiceProvider,
    Administrator,
    WasteReport,
    CollectionSchedule,
    RecyclingGuide,
    Notification,
    SystemLog,
)

admin.site.register(Resident)
admin.site.register(WasteServiceProvider)
admin.site.register(Administrator)
admin.site.register(WasteReport)
admin.site.register(CollectionSchedule)
admin.site.register(RecyclingGuide)
admin.site.register(Notification)
admin.site.register(SystemLog)