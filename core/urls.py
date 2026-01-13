from django.urls import path
from django.contrib.auth import views as auth_views

from .views import (
    home_view,
    signup_view,
    dashboard_view,
    doctor_availability_view,
    available_slots_view,
    book_slot_view,
    patient_bookings_view,
    connect_google_calendar,
    google_callback,
    logout_view,
)

urlpatterns = [
    path('', home_view, name='home'),

    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', dashboard_view, name='dashboard'),

    path('doctor/availability/', doctor_availability_view, name='doctor_availability'),

    path('patient/slots/', available_slots_view, name='available_slots'),
    path('patient/book/<int:slot_id>/', book_slot_view, name='book_slot'),
    path('patient/bookings/', patient_bookings_view, name='patient_bookings'),

    path('google/connect/', connect_google_calendar, name='google_connect'),
    path('google-callback/', google_callback, name='google_callback'),
]
