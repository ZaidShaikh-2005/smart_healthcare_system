from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views
from .forms import (
    LoginForm,
    MyPasswordChangeForm,
    MyPasswordResetForm,
    MySetPasswordForm,
)

urlpatterns = [

    # =====================================================
    # ROOT → ROLE BASED REDIRECT (LOGIN REQUIRED)
    # =====================================================
    path(
        "",
        views.home_redirect,
        name="home"
    ),

    # =====================================================
    # REGISTRATION ROLE SELECTION
    # =====================================================
    path(
        "select-registration/",
        auth_views.LoginView.as_view(
            template_name="app/auth/select_registration.html"
        ),
        name="select-registration"
    ),

    # =====================================================
    # REGISTRATION
    # =====================================================
    path(
        "register/",
        views.RegisterUserView.as_view(),
        name="registration"
    ),

    # =====================================================
    # AUTHENTICATION
    # =====================================================
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="app/auth/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True
        ),
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # =====================================================
    # PASSWORD MANAGEMENT
    # =====================================================
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="app/auth/passwordchange.html",
            form_class=MyPasswordChangeForm,
            success_url="/password/change/done/"
        ),
        name="passwordchange"
    ),

    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="app/auth/passwordchangedone.html"
        ),
        name="passwordchangedone"
    ),

    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name="app/auth/password_reset.html",
            form_class=MyPasswordResetForm
        ),
        name="password_reset"
    ),

    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="app/auth/password_reset_done.html"
        ),
        name="password_reset_done"
    ),

    path(
        "password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="app/auth/password_reset_confirm.html",
            form_class=MySetPasswordForm
        ),
        name="password_reset_confirm"
    ),

    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="app/auth/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),

    # =====================================================
    # PATIENT ROUTES
    # =====================================================
    path(
        "patient/dashboard/",
        views.patient_dashboard,
        name="patient-dashboard"
    ),

    path(
        "patient/profile/",
        views.patient_profile,
        name="patient-profile"
    ),

    path(
        "patient/records/add/",
        views.add_health_record,
        name="add-health-record"
    ),

    path(
        "patient/records/<int:record_id>/",
        views.record_detail,
        name="record-detail"
    ),

    # =====================================================
    # DOCTOR ROUTES
    # =====================================================
    path(
        "doctor/dashboard/",
        views.doctor_dashboard,
        name="doctor-dashboard"
    ),

    path(
        "doctor/patient/<int:patient_id>/",
        views.doctor_patient_detail,
        name="doctor-patient-detail"
    ),

    path(
        "doctors/",
        views.doctor_list,
        name="doctor-list"
    ),

    path(
        "book-appointment/<int:doctor_id>/",
        views.book_appointment,
        name="book-appointment"
    ),

    path(
        "doctor/profile/",
        views.DoctorProfileView.as_view(),
        name="doctor-profile"
    ),

    path(
        "doctor/profile/view/",
        views.doctor_view_profile,
        name="doctor-view-profile"
    ),
    path(
        "patient/profile/view/",
        views.patient_view_profile,
        name="patient-view-profile"
    ),

    path(
        "patient/ai-analyzer/",
        views.ai_analyzer,
        name="ai-analyzer"
    ),

    path("patient/symptoms/", views.patient_symptoms, name="patient-symptoms"),



]

# =====================================================
# MEDIA FILES (DEV ONLY)
# =====================================================
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)