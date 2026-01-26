from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


# ================= COMMON CHOICES =================

STATE_CHOICES = (
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("Arunachal Pradesh", "Arunachal Pradesh"),
    ("Assam", "Assam"),
    ("Bihar", "Bihar"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Goa", "Goa"),
    ("Gujarat", "Gujarat"),
    ("Haryana", "Haryana"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Jammu and Kashmir", "Jammu and Kashmir"),
    ("Jharkhand", "Jharkhand"),
    ("Karnataka", "Karnataka"),
    ("Kerala", "Kerala"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Maharashtra", "Maharashtra"),
    ("Manipur", "Manipur"),
    ("Meghalaya", "Meghalaya"),
    ("Mizoram", "Mizoram"),
    ("Nagaland", "Nagaland"),
    ("Odisha", "Odisha"),
    ("Punjab", "Punjab"),
    ("Rajasthan", "Rajasthan"),
    ("Sikkim", "Sikkim"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Tripura", "Tripura"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Uttarakhand", "Uttarakhand"),
    ("West Bengal", "West Bengal"),
    ("Delhi", "Delhi"),
    ("Puducherry", "Puducherry"),
)

GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other"),
)

ROLE_CHOICES = (
    ("PATIENT", "Patient"),
    ("DOCTOR", "Doctor"),
)

APPOINTMENT_STATUS = (
    ("PENDING", "Pending"),
    ("CONFIRMED", "Confirmed"),
    ("CANCELLED", "Cancelled"),
)


# ================= USER ROLE PROFILE =================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ================= PATIENT =================
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    patient_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # ✅ ADD ONLY THIS (NOTHING ELSE)
    photo = models.ImageField(
        upload_to="patient_photos/",
        blank=True,
        null=True
    )

    full_name = models.CharField(max_length=200, blank=True)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        null=True,
        blank=True
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    locality = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50, blank=True)
    zipcode = models.IntegerField(blank=True, null=True)
    state = models.CharField(
        max_length=50,
        choices=STATE_CHOICES,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    
# ================= HEALTH RECORD =================
class HealthRecord(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="records"
    )

    heart_rate = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(200)]
    )

    ecg = models.TextField(blank=True, null=True)

    # ✅ ADD THIS
    ecg_image = models.ImageField(
        upload_to="ecg_images/",
        blank=True,
        null=True
    )

    temperature = models.FloatField(
        validators=[MinValueValidator(30.0), MaxValueValidator(45.0)]
    )
    glucose_level = models.PositiveIntegerField(
        validators=[MinValueValidator(40), MaxValueValidator(500)]
    )
    oxygen_level = models.PositiveIntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(100)]
    )
    systolic_bp = models.PositiveIntegerField(
        validators=[MinValueValidator(70), MaxValueValidator(200)]
    )
    diastolic_bp = models.PositiveIntegerField(
        validators=[MinValueValidator(40), MaxValueValidator(130)]
    )
    weight = models.FloatField(
        validators=[MinValueValidator(2.0), MaxValueValidator(300.0)]
    )

    recorded_at = models.DateTimeField(auto_now_add=True)

# ================= DOCTOR =================
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100, blank=True)

    photo = models.ImageField(
        upload_to="doctor_photos/",
        blank=True,
        null=True
    )

    qualification = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    clinic_location = models.CharField(max_length=200, blank=True)

    available_days = models.CharField(
        max_length=50,
        blank=True
    )
    available_from = models.TimeField(
        null=True,
        blank=True
    )
    available_to = models.TimeField(
        null=True,
        blank=True
    )

    online_fee = models.PositiveIntegerField(
        default=0,
        blank=True
    )
    offline_fee = models.PositiveIntegerField(
        default=0,
        blank=True
    )

    def __str__(self):
        return self.full_name or self.user.username

# ================= APPOINTMENT =================
class Appointment(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(
        max_length=10,
        choices=APPOINTMENT_STATUS,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "appointment_date", "appointment_time")

    def __str__(self):
        return f"{self.patient} → {self.doctor}"


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class PatientSymptom(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="patient_symptoms"
    )
    symptom = models.ForeignKey(
        Symptom,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.symptom}"
