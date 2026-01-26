from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    AuthenticationForm,
    UsernameField,
    PasswordResetForm,
    PasswordChangeForm,
    SetPasswordForm
)
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation

from .models import (
    Patient,
    HealthRecord,
    Doctor,
)

# =====================================================
# USER REGISTRATION FORM
# =====================================================
class RegisterUserForm(forms.ModelForm):

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2:
            if password != password2:
                raise forms.ValidationError("Passwords do not match")
            password_validation.validate_password(password)

        return cleaned_data


# =====================================================
# LOGIN FORM
# =====================================================
class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={'autofocus': True, 'class': 'form-control'}
        )
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'current-password', 'class': 'form-control'}
        ),
    )


# =====================================================
# PASSWORD CHANGE
# =====================================================
class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Old Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password1 = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


# =====================================================
# PASSWORD RESET
# =====================================================
class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


# =====================================================
# PATIENT PROFILE FORM
# =====================================================
class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = [
            'user',
            'patient_id',
            'created_at',
            'photo',   # ❌ IMPORTANT: photo form se hata diya
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'locality': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'zipcode': forms.NumberInput(attrs={'class': 'form-control'}),
        }



# =====================================================
# HEALTH RECORD FORM
# =====================================================
class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        exclude = ['patient', 'recorded_at']
        widgets = {
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'ecg': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ecg_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control'}),
            'glucose_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'oxygen_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'systolic_bp': forms.NumberInput(attrs={'class': 'form-control'}),
            'diastolic_bp': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# =====================================================
# DOCTOR PROFILE FORM
# =====================================================

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "photo",
            "full_name",
            "qualification",
            "specialization",
            "clinic_location",
            "available_days",
            "available_from",
            "available_to",
            "online_fee",
            "offline_fee",
        ]

        widgets = {
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "available_from": forms.TimeInput(attrs={"type": "time"}),
            "available_to": forms.TimeInput(attrs={"type": "time"}),
        }
