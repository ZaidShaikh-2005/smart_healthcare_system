from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from .models import Doctor, UserProfile
import csv
from django.conf import settings
from pathlib import Path

from .models import (
    Patient,
    HealthRecord,
    UserProfile,
    Doctor,
    Appointment,
    PatientSymptom,
    Symptom,
)

from .forms import (
    RegisterUserForm,
    PatientProfileForm,
    HealthRecordForm,
    DoctorProfileForm,
)

# =====================================================
# HOME REDIRECT (ROLE BASED) → LOGIN REQUIRED
# =====================================================
@login_required
def home_redirect(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(
            request,
            "Account setup incomplete. Please login again."
        )
        logout(request)
        return redirect("login")

    if profile.role == "PATIENT":
        return redirect("patient-dashboard")

    if profile.role == "DOCTOR":
        return redirect("doctor-dashboard")

    messages.error(request, "Invalid user role.")
    logout(request)
    return redirect("login")


# =====================================================
# LOGOUT
# =====================================================
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


# =====================================================
# REGISTRATION
# =====================================================
class RegisterUserView(View):

    def get(self, request):
        role = request.GET.get("role")
        if role not in ["PATIENT", "DOCTOR"]:
            messages.error(request, "Please select a valid role.")
            return redirect("select-registration")

        return render(
            request,
            "app/auth/register.html",
            {"form": RegisterUserForm(), "role": role}
        )

    def post(self, request):
        role = request.GET.get("role")
        if role not in ["PATIENT", "DOCTOR"]:
            messages.error(request, "Invalid role.")
            return redirect("select-registration")

        form = RegisterUserForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # ✅ SAFE PROFILE CREATION
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={"role": role}
            )

            # If profile already exists, just update role
            if not created:
                profile.role = role
                profile.save()

            # ✅ SAFE ROLE OBJECT CREATION
            if role == "PATIENT":
                Patient.objects.get_or_create(user=user)

            elif role == "DOCTOR":
                Doctor.objects.get_or_create(
                    user=user,
                    defaults={"full_name": user.username}
                )

            messages.success(
                request,
                f"{role.capitalize()} registered successfully. Please login."
            )
            return redirect("login")

        return render(
            request,
            "app/auth/register.html",
            {"form": form, "role": role}
        )


# =====================================================
# PATIENT DASHBOARD (SAFE)
# =====================================================
@login_required
def patient_dashboard(request):
    get_object_or_404(
        UserProfile,
        user=request.user,
        role="PATIENT"
    )

    patient, _ = Patient.objects.get_or_create(
        user=request.user
    )

    records = HealthRecord.objects.filter(
        patient=patient
    ).order_by("-recorded_at")

    # 🔥 ADD THIS
    selected_symptoms = Symptom.objects.filter(
        patientsymptom__patient=patient
    )

    return render(
        request,
        "app/patient/dashboard.html",
        {
            "patient": patient,
            "records": records,
            "latest_record": records.first(),
            "selected_symptoms": selected_symptoms,
        }
    )


# =====================================================
# ADD HEALTH RECORD
# =====================================================
@login_required
def add_health_record(request):
    get_object_or_404(
        UserProfile,
        user=request.user,
        role="PATIENT"
    )

    patient = get_object_or_404(Patient, user=request.user)

    if request.method == "POST":
        print("FILES 👉", request.FILES)  # DEBUG (yahan image dikhegi)

        form = HealthRecordForm(
            request.POST,
            request.FILES   # 🔥 MOST IMPORTANT LINE
        )

        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.save()

            messages.success(request, "Health record added successfully")
            return redirect("patient-dashboard")
        else:
            print("FORM ERRORS 👉", form.errors)

    else:
        form = HealthRecordForm()

    return render(
        request,
        "app/patient/add_record.html",
        {"form": form}
    )


# =====================================================
# RECORD DETAIL
# =====================================================
@login_required
def record_detail(request, record_id):
    get_object_or_404(
        UserProfile,
        user=request.user,
        role="PATIENT"
    )

    record = get_object_or_404(
        HealthRecord,
        id=record_id,
        patient__user=request.user
    )

    return render(
        request,
        "app/patient/record_detail.html",
        {"record": record}
    )


# =====================================================
# DOCTOR DASHBOARD
# =====================================================
@login_required
def doctor_dashboard(request):
    get_object_or_404(
        UserProfile,
        user=request.user,
        role="DOCTOR"
    )

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).order_by("-appointment_date", "-appointment_time")

    return render(
        request,
        "app/doctor/dashboard.html",
        {
            "doctor": doctor,
            "appointments": appointments,
        }
    )


# =====================================================
# DOCTOR → PATIENT DETAIL (SECURE)
# =====================================================
@login_required
def doctor_patient_detail(request, patient_id):
    get_object_or_404(
        UserProfile,
        user=request.user,
        role="DOCTOR"
    )

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    appointment = get_object_or_404(
        Appointment,
        doctor=doctor,
        patient__id=patient_id
    )

    patient = appointment.patient

    records = HealthRecord.objects.filter(
        patient=patient
    ).order_by("-recorded_at")

    return render(
        request,
        "app/doctor/patient_detail.html",
        {
            "patient": patient,
            "records": records
        }
    )

@login_required
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(
        request,
        "app/appointments/doctor_list.html",
        {"doctors": doctors}
    )

@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient = get_object_or_404(Patient, user=request.user)

    if request.method == "POST":
        appointment_date = request.POST.get("appointment_date")
        appointment_time = request.POST.get("appointment_time")

        if not appointment_date or not appointment_time:
            messages.error(request, "Please select date and time")
            return redirect(request.path)

        Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status="CONFIRMED"
        )

        messages.success(request, "Appointment booked successfully")
        return redirect("patient-dashboard")

    return render(
        request,
        "app/patient/book_appointment.html",
        {"doctor": doctor}
    )

# views.py
@login_required
def doctor_profile(request):
    get_object_or_404(UserProfile, user=request.user, role="DOCTOR")

    doctor, _ = Doctor.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.username}
    )

    if request.method == "POST":
        form = DoctorProfileForm(
            request.POST,
            request.FILES,
            instance=doctor
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("doctor-dashboard")
    else:
        form = DoctorProfileForm(instance=doctor)

    return render(
        request,
        "app/doctor/profile.html",
        {
            "form": form,
            "doctor": doctor
        }
    )


@method_decorator(login_required, name="dispatch")
@method_decorator(login_required, name="dispatch")
class DoctorProfileView(View):

    def get(self, request):
        get_object_or_404(
            UserProfile,
            user=request.user,
            role="DOCTOR"
        )

        doctor, _ = Doctor.objects.get_or_create(
            user=request.user,
            defaults={
                "full_name": request.user.get_full_name() or request.user.username
            }
        )

        form = DoctorProfileForm(instance=doctor)

        first_letter = (
            doctor.full_name[0].upper()
            if doctor.full_name
            else request.user.username[0].upper()
        )

        return render(
            request,
            "app/doctor/profile.html",
            {
                "form": form,
                "doctor": doctor,
                "first_letter": first_letter,
            }
        )

    def post(self, request):
        get_object_or_404(
            UserProfile,
            user=request.user,
            role="DOCTOR"
        )

        doctor = get_object_or_404(Doctor, user=request.user)

        form = DoctorProfileForm(
            request.POST,
            request.FILES,
            instance=doctor
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Doctor profile updated successfully ✅"
            )
            return redirect("doctor-dashboard")

        first_letter = (
            doctor.full_name[0].upper()
            if doctor.full_name
            else request.user.username[0].upper()
        )

        return render(
            request,
            "app/doctor/profile.html",
            {
                "form": form,
                "doctor": doctor,
                "first_letter": first_letter,
            }
        )
    
@login_required
def doctor_view_profile(request):
    # ensure logged-in user is a doctor
    get_object_or_404(
        UserProfile,
        user=request.user,
        role="DOCTOR"
    )

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    return render(
        request,
        "app/doctor/view_profile.html",
        {
            "doctor": doctor
        }
    )

@login_required
def patient_profile(request):
    patient = get_object_or_404(Patient, user=request.user)

    if request.method == "POST":
        print("FILES 👉", request.FILES)  # DEBUG (ab yahan photo dikhegi)

        form = PatientProfileForm(request.POST, instance=patient)

        if form.is_valid():
            patient = form.save(commit=False)

            # 🔥 PHOTO SAVE (IMPORTANT)
            if "photo" in request.FILES:
                patient.photo = request.FILES["photo"]

            patient.save()
            messages.success(request, "Profile updated successfully")
            return redirect("patient-profile")

    else:
        form = PatientProfileForm(instance=patient)

    return render(
        request,
        "app/patient/profile.html",
        {
            "form": form,
            "patient": patient
        }
    )

@login_required
def patient_view_profile(request):
    # ensure logged-in user is a patient
    get_object_or_404(
        UserProfile,
        user=request.user,
        role="PATIENT"
    )

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    return render(
        request,
        "app/patient/view_profile.html",
        {
            "patient": patient
        }
    )

@login_required
def ai_analyzer(request):
    get_object_or_404(UserProfile, user=request.user, role="PATIENT")
    patient = get_object_or_404(Patient, user=request.user)

    # Patient symptoms
    patient_symptoms = PatientSymptom.objects.filter(
        patient=patient
    ).select_related("symptom")

    selected_symptom_names = set(
        ps.symptom.name.lower() for ps in patient_symptoms
    )

    predictions = []

import csv
import re
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from app.models import Patient, PatientSymptom, UserProfile


# 🔹 Helper: normalize symptom names
def normalize(symptom: str) -> str:
    """
    fever, Fever, fever_, fever  -> fever
    joint pain -> joint_pain
    dischromic _patches -> dischromic_patches
    """
    symptom = symptom.lower().strip()
    symptom = re.sub(r"\s+", "_", symptom)
    symptom = re.sub(r"_+", "_", symptom)
    return symptom


@login_required
def ai_analyzer(request):
    # ================= USER CHECK =================
    get_object_or_404(UserProfile, user=request.user, role="PATIENT")
    patient = get_object_or_404(Patient, user=request.user)

    # ================= PATIENT SYMPTOMS =================
    patient_symptoms = PatientSymptom.objects.filter(
        patient=patient
    ).select_related("symptom")

    selected_symptoms = {
        normalize(ps.symptom.name)
        for ps in patient_symptoms
    }

    predictions = []
    high_risk = False

    # ================= PATHS =================
    base_path = Path(settings.BASE_DIR) / "archive"

    disease_symptom_csv = base_path / "dataset.csv"
    description_csv = base_path / "symptom_Description.csv"
    precaution_csv = base_path / "symptom_precaution.csv"
    severity_csv = base_path / "Symptom-severity.csv"

    # ================= DATA CONTAINERS =================
    disease_map = {}
    descriptions = {}
    precautions = {}
    symptom_weight = {}

    # ================= LOAD DISEASE ↔ SYMPTOMS =================
    with open(disease_symptom_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            disease = row["Disease"].strip()

            symptoms = set()
            for col in row:
                if col.startswith("Symptom") and row[col]:
                    symptoms.add(normalize(row[col]))

            disease_map[disease] = symptoms

    # ================= LOAD DESCRIPTIONS =================
    with open(description_csv, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                descriptions[row[0].strip()] = row[1].strip()

    # ================= LOAD PRECAUTIONS =================
    with open(precaution_csv, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            precautions[row[0].strip()] = [p for p in row[1:] if p]

    # ================= LOAD SEVERITY (HEADER SAFE) =================
    with open(severity_csv, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # header skip

        for row in reader:
            if len(row) >= 2:
                try:
                    symptom_weight[normalize(row[0])] = int(row[1])
                except ValueError:
                    continue

    # ================= PROBABILITY LOGIC =================
    for disease, disease_symptoms in disease_map.items():

        matched = set()

        # 🔹 SOFT MATCH (exact + partial)
        for s in selected_symptoms:
            for ds in disease_symptoms:
                if s == ds or s in ds or ds in s:
                    matched.add(ds)

        if not matched:
            continue

        # 🔹 Severity weighted score
        weighted_score = sum(
            symptom_weight.get(sym, 1)
            for sym in matched
        )

        max_score = sum(
            symptom_weight.get(sym, 1)
            for sym in disease_symptoms
        )

        raw_score = weighted_score / max_score
        probability = min(int(raw_score * 100), 95)

        predictions.append({
            "disease": disease,
            "probability": probability,
            "matched": list(matched),
            "description": descriptions.get(
                disease, "No description available."
            ),
            "precautions": precautions.get(disease, []),
        })

    # ================= NO MATCH FALLBACK =================
    if not predictions:
        return render(
            request,
            "app/patient/ai_analyzer.html",
            {
                "patient": patient,
                "predictions": [],
                "high_risk": False,
            }
        )

    # ================= NORMALIZE CONFIDENCE (SUM = 100) =================
    total = sum(p["probability"] for p in predictions)

    for p in predictions:
        p["probability"] = round((p["probability"] / total) * 100, 1)

    # ================= SORT + TOP 3 =================
    predictions.sort(key=lambda x: x["probability"], reverse=True)
    predictions = predictions[:3]

    # ================= HIGH RISK =================
    if predictions[0]["probability"] >= 70:
        high_risk = True

    return render(
        request,
        "app/patient/ai_analyzer.html",
        {
            "patient": patient,
            "predictions": predictions,
            "high_risk": high_risk,
        }
    )

@login_required
def patient_symptoms(request):
    patient = get_object_or_404(Patient, user=request.user)
    symptoms = Symptom.objects.all()

    if request.method == "POST":
        selected = request.POST.getlist("symptoms")

        # 🔥 purane symptoms delete
        PatientSymptom.objects.filter(patient=patient).delete()

        # 🔥 naye symptoms insert
        bulk_data = [
            PatientSymptom(
                patient=patient,
                symptom_id=sid
            )
            for sid in selected
        ]
        PatientSymptom.objects.bulk_create(bulk_data)

        messages.success(request, "Symptoms saved successfully")
        return redirect("patient-dashboard")

    # ✅ selected symptoms IDs
    selected_ids = PatientSymptom.objects.filter(
        patient=patient
    ).values_list("symptom_id", flat=True)

    return render(
        request,
        "app/patient/symptoms.html",
        {
            "symptoms": symptoms,
            "selected_ids": selected_ids
        }
    )
