from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from datetime import datetime, timedelta, date, time
from extensions import db
from models import Business, Service, WorkingHour, Booking
from forms import BookingForm

booking_bp = Blueprint("booking", __name__)

def get_available_slots(business, service, booking_date):
    day_of_week = booking_date.weekday()
    working_hour = WorkingHour.query.filter_by(
        business_id=business.id,
        day_of_week=day_of_week
    ).first()
    
    if not working_hour or working_hour.is_closed:
        return []
    
    slots = []
    current_time = datetime.combine(booking_date, working_hour.open_time)
    end_time = datetime.combine(booking_date, working_hour.close_time)
    slot_duration = timedelta(minutes=service.duration_minutes)
    
    existing_bookings = Booking.query.filter(
        Booking.business_id == business.id,
        Booking.booking_date == booking_date,
        Booking.status.in_(["pending", "confirmed"])
    ).all()
    
    while current_time + slot_duration <= end_time:
        slot_start = current_time.time()
        slot_end = (current_time + slot_duration).time()
        
        is_available = True
        for booking in existing_bookings:
            booking_start = booking.booking_time
            booking_end = booking.end_time
            
            if not (slot_end <= booking_start or slot_start >= booking_end):
                is_available = False
                break
        
        if is_available:
            if booking_date > date.today() or (booking_date == date.today() and slot_start > datetime.now().time()):
                slots.append(slot_start.strftime("%H:%M"))
        
        current_time += timedelta(minutes=30)
    
    return slots

@booking_bp.route("/<slug>/")
def public_page(slug):
    business = Business.query.filter_by(slug=slug, is_active=True).first_or_404()
    services = Service.query.filter_by(business_id=business.id, is_active=True).order_by(Service.name).all()
    working_hours = WorkingHour.query.filter_by(business_id=business.id).order_by(WorkingHour.day_of_week).all()
    return render_template("booking/public_page.html", business=business, services=services, working_hours=working_hours)

@booking_bp.route("/<slug>/book", methods=["GET", "POST"])
def book(slug):
    business = Business.query.filter_by(slug=slug, is_active=True).first_or_404()
    services = Service.query.filter_by(business_id=business.id, is_active=True).order_by(Service.name).all()
    
    if not services:
        flash("No services available for booking.", "error")
        return redirect(url_for("booking.public_page", slug=slug))
    
    form = BookingForm()
    form.service_id.choices = [(s.id, f"{s.name} - ${s.price} ({s.duration_minutes} min)") for s in services]
    form.booking_time.choices = []
    
    selected_service_id = request.args.get("service_id", type=int) or (services[0].id if services else None)
    selected_date = request.args.get("date", "")
    
    if request.method == "POST":
        service_id = form.service_id.data
        booking_date_str = request.form.get("booking_date", "")
        if service_id and booking_date_str:
            try:
                booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
                service = Service.query.get(service_id)
                if service and service.business_id == business.id:
                    slots = get_available_slots(business, service, booking_date)
                    form.booking_time.choices = [(s, s) for s in slots]
            except ValueError:
                pass
    elif selected_service_id and selected_date:
        try:
            booking_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            service = Service.query.get(selected_service_id)
            if service and service.business_id == business.id:
                slots = get_available_slots(business, service, booking_date)
                form.booking_time.choices = [(s, s) for s in slots]
        except ValueError:
            pass
    
    if form.validate_on_submit():
        service = Service.query.filter_by(id=form.service_id.data, business_id=business.id).first()
        if not service:
            flash("Invalid service selected.", "error")
            return redirect(url_for("booking.book", slug=slug))
        
        booking_time = datetime.strptime(form.booking_time.data, "%H:%M").time()
        
        slots = get_available_slots(business, service, form.booking_date.data)
        if form.booking_time.data not in slots:
            flash("This time slot is no longer available.", "error")
            return redirect(url_for("booking.book", slug=slug))
        
        booking = Booking(
            business_id=business.id,
            service_id=service.id,
            customer_name=form.customer_name.data,
            customer_phone=form.customer_phone.data,
            customer_email=form.customer_email.data,
            booking_date=form.booking_date.data,
            booking_time=booking_time,
            notes=form.notes.data,
            status="pending"
        )
        db.session.add(booking)
        db.session.commit()
        
        return redirect(url_for("booking.confirmation", slug=slug, booking_id=booking.id))
    
    return render_template("booking/book.html", form=form, business=business, services=services,
                         selected_service_id=selected_service_id, selected_date=selected_date)

@booking_bp.route("/<slug>/slots")
def get_slots(slug):
    business = Business.query.filter_by(slug=slug, is_active=True).first_or_404()
    service_id = request.args.get("service_id", type=int)
    date_str = request.args.get("date")
    
    if not service_id or not date_str:
        return jsonify({"slots": []})
    
    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"slots": []})
    
    service = Service.query.filter_by(id=service_id, business_id=business.id).first()
    if not service:
        return jsonify({"slots": []})
    
    slots = get_available_slots(business, service, booking_date)
    return jsonify({"slots": slots})

@booking_bp.route("/<slug>/confirmation/<int:booking_id>")
def confirmation(slug, booking_id):
    business = Business.query.filter_by(slug=slug).first_or_404()
    booking = Booking.query.filter_by(id=booking_id, business_id=business.id).first_or_404()
    return render_template("booking/confirmation.html", business=business, booking=booking)
