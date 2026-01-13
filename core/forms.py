from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect  # Added redirect
# Removed redundant imports and combined them below
from .models import AvailabilitySlot, DoctorProfile 

# --- FORMS ---

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient')
    ])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

# --- VIEWS ---

# Note: You need to define or import @doctor_required. 
# If you haven't created it yet, I've used a standard test below.
from django.contrib.auth.decorators import user_passes_test

def is_doctor(user):
    return hasattr(user, 'doctorprofile') # Adjust based on your logic

@login_required
@user_passes_test(is_doctor)
def doctor_availability_view(request):
    # Use get_or_create or a try/except to prevent 404/500 errors
    doctor = DoctorProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = doctor
            slot.save()
            return redirect('doctor_availability_view') # Make sure this name matches your urls.py
    else:
        form = AvailabilityForm()

    slots = AvailabilitySlot.objects.filter(doctor=doctor).order_by('date', 'start_time')

    return render(
        request,
        'doctor_availability.html',
        {
            'form': form,
            'slots': slots
        }
    )