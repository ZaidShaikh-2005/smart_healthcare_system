from django.contrib import admin
from .models import (
    Patient,
    HealthRecord,
    Doctor,
    UserProfile,
    Appointment
)

# ================= HEALTH RECORD INLINE =================
class HealthRecordInline(admin.TabularInline):
    model = HealthRecord
    extra = 0
    readonly_fields = ('recorded_at',)
    ordering = ('-recorded_at',)


# ================= USER PROFILE =================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)


# ================= PATIENT =================
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'full_name',
        'age',
        'gender',
        'city',
        'state',
    )

    search_fields = (
        'full_name',
        'user__username',
        'user__email'
    )

    list_filter = (
        'gender',
        'state',
        'city'
    )

    ordering = ('full_name',)

    inlines = [HealthRecordInline]


# ================= HEALTH RECORD =================
@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'patient',
        'heart_rate',
        'oxygen_level',
        'glucose_level',
        'systolic_bp',
        'diastolic_bp',
        'recorded_at'
    )

    list_filter = ('recorded_at',)

    search_fields = (
        'patient__full_name',
        'patient__user__username'
    )

    readonly_fields = ('recorded_at',)

    ordering = ('-recorded_at',)


# ================= DOCTOR =================
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'full_name',
        'specialization',
        'clinic_location',
        'available_days',
        'available_from',
        'available_to',
        'online_fee',
        'offline_fee',
    )

    search_fields = (
        'full_name',
        'specialization',
        'clinic_location'
    )

    list_filter = ('specialization',)

    ordering = ('full_name',)


# ================= APPOINTMENT =================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'doctor',
        'patient',
        'appointment_date',
        'appointment_time',
    )

    list_filter = (
        'appointment_date',
    )

    search_fields = (
        'doctor__full_name',
        'patient__full_name'
    )

    ordering = ('-appointment_date', '-appointment_time')
