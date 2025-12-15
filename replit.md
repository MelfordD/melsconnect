# Mel's Connect - Multi-Tenant Booking Platform

## Overview
Mel's Connect is a multi-tenant booking platform built with Flask that allows multiple businesses (salons, clinics, gyms, barbers) to have their own booking pages and dashboards.

## Tech Stack
- **Backend**: Flask with Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: PostgreSQL
- **Frontend**: Jinja2 templates with Tailwind CSS (via CDN)
- **Authentication**: Flask-Login with password hashing

## Project Structure
```
├── app.py              # Main Flask application
├── models.py           # Database models (User, Business, Service, WorkingHour, Booking)
├── forms.py            # WTForms for validation
├── seed_admin.py       # Script to create admin user
├── routes/
│   ├── main.py         # Home page routes
│   ├── auth.py         # Authentication routes
│   ├── dashboard.py    # Business owner dashboard
│   ├── booking.py      # Public booking pages
│   └── admin.py        # Admin panel routes
├── templates/
│   ├── base.html       # Base template
│   ├── index.html      # Homepage
│   ├── auth/           # Login and register templates
│   ├── dashboard/      # Business owner dashboard templates
│   ├── booking/        # Public booking page templates
│   └── admin/          # Admin panel templates
└── static/             # Static files
```

## Key Features
- **Multi-tenant architecture**: Each business isolated by unique slug
- **Role-based access**: Admin (superuser), Business Owner, Customer
- **Business Management**: Create/edit businesses, manage services, set working hours
- **Booking System**: Conflict prevention, real-time availability slots
- **Admin Panel**: Manage all users, businesses, and view all bookings

## Running the Application
The application runs on port 5000 with `python app.py`.

To create an admin user, run:
```bash
python seed_admin.py
```

Default admin credentials:
- Email: admin@melsconnect.com
- Password: admin123

## Database Models
- **User**: Platform users (admins and business owners)
- **Business**: Business profiles with slug, owner, contact info
- **Service**: Services offered by businesses (name, price, duration)
- **WorkingHour**: Business operating hours per day
- **Booking**: Customer appointments with status tracking

## URL Routes
- `/` - Homepage
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/dashboard/` - Business owner dashboard
- `/b/<slug>/` - Public business booking page
- `/b/<slug>/book` - Booking form
- `/admin/` - Admin panel

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SESSION_SECRET` - Flask session secret key

## Recent Changes
- Initial build: Complete MVP with all core features
