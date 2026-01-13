from django.contrib import admin
from .models import (
    UserProfile,
    DoctorProfile,
    PatientProfile,
    AvailabilitySlot,
    Booking
)

admin.site.register(UserProfile)
admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)
admin.site.register(AvailabilitySlot)
admin.site.register(Booking)
