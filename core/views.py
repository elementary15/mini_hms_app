import os
from datetime import datetime
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db import transaction

from google_auth_oauthlib.flow import Flow

# Local Imports
from .google_calendar import load_credentials_for_user, create_calendar_event
from .email_service import send_email
from .models import (
    UserProfile,
    DoctorProfile,
    PatientProfile,
    AvailabilitySlot,
    Booking
)
from .forms import SignupForm, AvailabilityForm

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return redirect('home')


# =========================
# AUTH & DASHBOARD
# =========================
def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def signup_view(request):
    if request.user.is_authenticated:
        logout(request)

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            role = form.cleaned_data['role']
            UserProfile.objects.create(user=user, role=role)

            if role == 'DOCTOR':
                DoctorProfile.objects.create(user=user)
            else:
                PatientProfile.objects.create(user=user)

            login(request, user)

            # STEP 8.1 — Send Welcome Email
            send_email("SIGNUP_WELCOME", user.email)

            return redirect('dashboard')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import os


@login_required
def connect_google_calendar(request):
    flow = Flow.from_client_secrets_file(
        '/etc/secrets/credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri='http://localhost:8001/google-callback/'
    )

    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )

    # DO NOT store state manually
    return redirect(authorization_url)


@login_required
def google_callback(request):
    flow = Flow.from_client_secrets_file(
        '/etc/secrets/credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri='http://localhost:8001/google-callback/'
    )

    # This must be the FULL callback URL
    authorization_response = request.build_absolute_uri()

    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials

    os.makedirs('google_tokens', exist_ok=True)
    with open(f'google_tokens/user_{request.user.id}.json', 'w') as token:
        token.write(creds.to_json())

    return redirect('dashboard')

@login_required
def dashboard_view(request):
    profile = UserProfile.objects.get(user=request.user)

    if profile.role == 'DOCTOR':
        return render(request, 'doctor_dashboard.html')
    else:
        return render(request, 'patient_dashboard.html')


# =========================
# ROLE GUARDS
# =========================

def doctor_required(view_func):
    def wrapper(request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'DOCTOR':
            return HttpResponseForbidden("Doctors only")
        return view_func(request, *args, **kwargs)
    return wrapper


def patient_required(view_func):
    def wrapper(request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'PATIENT':
            return HttpResponseForbidden("Patients only")
        return view_func(request, *args, **kwargs)
    return wrapper


# =========================
# DOCTOR VIEWS
# =========================

@login_required
@doctor_required
def doctor_availability_view(request):
    doctor = DoctorProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = doctor
            slot.save()
            messages.success(request, "Availability slot added successfully.")
        return redirect('doctor_availability')

    else:
        form = AvailabilityForm()

    slots = AvailabilitySlot.objects.filter(
        doctor=doctor
    ).order_by('date', 'start_time')

    return render(
        request,
        'doctor_availability.html',
        {
            'form': form,
            'slots': slots
        }
    )


# =========================
# PATIENT VIEWS
# =========================

@login_required
@patient_required
def available_slots_view(request):
    today = timezone.now().date()

    slots = AvailabilitySlot.objects.filter(
        is_booked=False,
        date__gte=today
    )

    print("SLOTS FOUND:", slots.count())

    return render(
        request,
        'available_slots.html',
        {'slots': slots}
    )



@login_required
@patient_required
def book_slot_view(request, slot_id):
    patient = PatientProfile.objects.get(user=request.user)

    try:
        with transaction.atomic():
            slot = AvailabilitySlot.objects.select_for_update().get(
                id=slot_id,
                is_booked=False
            )

            # Prevent duplicate booking at DB level
            booking, created = Booking.objects.get_or_create(
                slot=slot,
                defaults={
                    "doctor": slot.doctor,
                    "patient": patient
                }
            )

            if not created:
                return HttpResponseForbidden("This slot is already booked.")

            slot.is_booked = True
            slot.save()

            # =========================
            # GOOGLE CALENDAR EVENTS
            # =========================
            start_dt = datetime.combine(slot.date, slot.start_time)
            end_dt = datetime.combine(slot.date, slot.end_time)

            doctor_creds = load_credentials_for_user(slot.doctor.user.id)
            if doctor_creds:
                create_calendar_event(
                    doctor_creds,
                    title=f"Appointment with {patient.user.username}",
                    description="Hospital Management System Appointment",
                    start_dt=start_dt,
                    end_dt=end_dt
                )

            patient_creds = load_credentials_for_user(patient.user.id)
            if patient_creds:
                create_calendar_event(
                    patient_creds,
                    title=f"Appointment with Dr. {slot.doctor.user.username}",
                    description="Hospital Management System Appointment",
                    start_dt=start_dt,
                    end_dt=end_dt
                )

            send_email(
                "BOOKING_CONFIRMATION",
                patient.user.email,
                data={
                    "doctor": f"Dr. {slot.doctor.user.username}",
                    "date": str(slot.date),
                    "time": f"{slot.start_time} - {slot.end_time}"
                }
            )

    except AvailabilitySlot.DoesNotExist:
        return HttpResponseForbidden("Slot already booked or does not exist.")
    messages.success(request, "Appointment booked successfully.")

    return redirect('patient_bookings')

@login_required
@patient_required
def patient_bookings_view(request):
    patient = PatientProfile.objects.get(user=request.user)

    bookings = Booking.objects.filter(
        patient=patient
    ).select_related('doctor', 'slot')

    return render(
        request,
        'patient_bookings.html',
        {'bookings': bookings}
    )