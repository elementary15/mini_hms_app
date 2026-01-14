# Mini Hospital Management System (HMS)

A role-based hospital appointment scheduling system built using **Django**, designed to simulate real-world workflows between doctors and patients. The system focuses on **correctness, safety, and clarity** rather than overengineering.

This project was developed as part of the **SLS Python Developer Intern Task**.

---

## 🚀 Project Overview

Mini HMS allows:

* **Doctors** to manage their availability
* **Patients** to book appointments
* Automatic synchronization with **Google Calendar**
* Email notifications for key actions

The system enforces real-world constraints such as:

* No double booking
* Immutable booked slots
* Role-based access control

---

## 👥 User Roles

### Doctor

* Sign up / Login
* Connect Google Calendar
* Create availability slots
* Edit or delete **unbooked** slots
* View booked slots with patient details
* See appointments auto-added to Google Calendar

### Patient

* Sign up / Login
* View available appointment slots
* Book an appointment
* View booked appointments
* See appointments auto-added to Google Calendar
* Receive booking confirmation email

---

## ✨ Key Features

* Role-based authentication (Doctor / Patient)
* Safe appointment booking using database transactions
* Slot-level locking to prevent race conditions
* Google Calendar integration for both doctors and patients
* Email notifications via a decoupled email service
* Clean and modern UI with role-aware navigation

---

## 🧱 Tech Stack

* **Backend:** Django 6.x (Python)
* **Database:** SQLite (local)
* **Auth:** Django built-in authentication
* **Calendar Integration:** Google Calendar API (OAuth 2.0)
* **Email Service:** Separate HTTP-based email microservice
* **Frontend:** Django Templates (HTML + CSS)

---

## 🧠 Architecture & Flow

### High-Level Flow

1. User signs up and selects a role
2. Doctor creates availability slots
3. Patient views and books available slots
4. Booking is handled inside a database transaction
5. Slot is locked and marked as booked
6. Calendar events are created for both users
7. Email notifications are sent asynchronously

### Booking Safety

* Uses `select_for_update()` to prevent double booking
* Slot-to-booking relationship is one-to-one
* Backend guards prevent editing or deleting booked slots

---

## 🔒 Design Decisions (Important)

### Why booked slots cannot be edited or deleted

Once a slot is booked, modifying it could:

* Break patient commitments
* Desync calendar events
* Require cascading notifications

To keep booking guarantees strong, booked slots are treated as **immutable**.

### Why patient cancellation is not implemented

Patient-driven cancellation requires:

* Calendar event deletion
* Slot re-opening logic
* Email notifications to doctors
* Conflict handling

This was intentionally scoped out to avoid partial or unsafe behavior.

### Why email failures don’t break the system

The email service is decoupled. If email delivery fails, the core booking flow still succeeds.

---

## ▶️ How to Run Locally

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run migrations

```bash
python manage.py migrate
```

5. Start the Django server

```bash
python manage.py runserver 8001
```

6. (Optional) Start the email service separately

---

## 🧪 Testing

The system has been tested end-to-end for:

* Doctor workflow
* Patient workflow
* Booking integrity
* Calendar sync
* Email notifications

Manual A–Z testing was performed using multiple browser sessions.

---

## 🔮 Future Improvements

* Patient appointment cancellation with notifications
* HTML-rich email templates
* Deployment with secure HTTPS (required for OAuth in production)
* Admin analytics dashboard
* Pagination and filtering for slots

---

## 👤 Author

**Shamanth Vasishta**

This project demonstrates backend fundamentals, system design judgment, and practical integration of third-party services.

---

## 📌 Notes

* Google Calendar integration requires HTTPS in production
* OAuth credentials must be configured per environment

---

Thank you for reviewing this project.
