from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime, timedelta, time
from app import db
from models import Business, Service, WorkingHour, Booking
from forms import BusinessForm, ServiceForm, WorkingHourForm, BookingStatusForm

dashboard_bp = Blueprint("dashboard", __name__)

def get_user_business():
    business = Business.query.filter_by(owner_id=current_user.id).first()
    return business

@dashboard_bp.route("/")
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    today = datetime.now().date()
    upcoming_bookings = Booking.query.filter(
        Booking.business_id == business.id,
        Booking.booking_date >= today,
        Booking.status.in_(["pending", "confirmed"])
    ).order_by(Booking.booking_date, Booking.booking_time).limit(5).all()
    
    total_bookings = Booking.query.filter_by(business_id=business.id).count()
    pending_count = Booking.query.filter_by(business_id=business.id, status="pending").count()
    services_count = Service.query.filter_by(business_id=business.id, is_active=True).count()
    
    return render_template("dashboard/index.html", 
                         business=business, 
                         upcoming_bookings=upcoming_bookings,
                         total_bookings=total_bookings,
                         pending_count=pending_count,
                         services_count=services_count)

@dashboard_bp.route("/business/create", methods=["GET", "POST"])
@login_required
def create_business():
    if get_user_business():
        flash("You already have a business.", "info")
        return redirect(url_for("dashboard.index"))
    
    form = BusinessForm()
    if form.validate_on_submit():
        business = Business(
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            description=form.description.data,
            owner_id=current_user.id
        )
        business.generate_slug()
        db.session.add(business)
        db.session.commit()
        
        for day in range(7):
            if day < 5:
                wh = WorkingHour(
                    business_id=business.id,
                    day_of_week=day,
                    open_time=time(9, 0),
                    close_time=time(17, 0),
                    is_closed=False
                )
            else:
                wh = WorkingHour(
                    business_id=business.id,
                    day_of_week=day,
                    open_time=time(9, 0),
                    close_time=time(17, 0),
                    is_closed=True
                )
            db.session.add(wh)
        db.session.commit()
        
        flash("Business created successfully!", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("dashboard/create_business.html", form=form)

@dashboard_bp.route("/business/edit", methods=["GET", "POST"])
@login_required
def edit_business():
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    form = BusinessForm(obj=business)
    if form.validate_on_submit():
        business.name = form.name.data
        business.phone = form.phone.data
        business.address = form.address.data
        business.description = form.description.data
        db.session.commit()
        flash("Business updated successfully!", "success")
        return redirect(url_for("dashboard.index"))
    return render_template("dashboard/edit_business.html", form=form, business=business)

@dashboard_bp.route("/services")
@login_required
def services():
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    services = Service.query.filter_by(business_id=business.id).order_by(Service.name).all()
    return render_template("dashboard/services.html", services=services, business=business)

@dashboard_bp.route("/services/add", methods=["GET", "POST"])
@login_required
def add_service():
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(
            business_id=business.id,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            duration_minutes=form.duration_minutes.data
        )
        db.session.add(service)
        db.session.commit()
        flash("Service added successfully!", "success")
        return redirect(url_for("dashboard.services"))
    return render_template("dashboard/service_form.html", form=form, business=business, title="Add Service")

@dashboard_bp.route("/services/<int:service_id>/edit", methods=["GET", "POST"])
@login_required
def edit_service(service_id):
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    service = Service.query.filter_by(id=service_id, business_id=business.id).first_or_404()
    form = ServiceForm(obj=service)
    if form.validate_on_submit():
        service.name = form.name.data
        service.description = form.description.data
        service.price = form.price.data
        service.duration_minutes = form.duration_minutes.data
        db.session.commit()
        flash("Service updated successfully!", "success")
        return redirect(url_for("dashboard.services"))
    return render_template("dashboard/service_form.html", form=form, business=business, service=service, title="Edit Service")

@dashboard_bp.route("/services/<int:service_id>/delete", methods=["POST"])
@login_required
def delete_service(service_id):
    business = get_user_business()
    if not business:
        abort(404)
    
    service = Service.query.filter_by(id=service_id, business_id=business.id).first_or_404()
    service.is_active = False
    db.session.commit()
    flash("Service deleted successfully!", "success")
    return redirect(url_for("dashboard.services"))

@dashboard_bp.route("/hours")
@login_required
def working_hours():
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    hours = WorkingHour.query.filter_by(business_id=business.id).order_by(WorkingHour.day_of_week).all()
    return render_template("dashboard/working_hours.html", hours=hours, business=business)

@dashboard_bp.route("/hours/<int:hour_id>/edit", methods=["GET", "POST"])
@login_required
def edit_working_hour(hour_id):
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    hour = WorkingHour.query.filter_by(id=hour_id, business_id=business.id).first_or_404()
    form = WorkingHourForm(obj=hour)
    if form.validate_on_submit():
        hour.open_time = form.open_time.data
        hour.close_time = form.close_time.data
        hour.is_closed = form.is_closed.data
        db.session.commit()
        flash("Working hours updated!", "success")
        return redirect(url_for("dashboard.working_hours"))
    return render_template("dashboard/edit_hour.html", form=form, hour=hour, business=business)

@dashboard_bp.route("/bookings")
@login_required
def bookings():
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    status_filter = request.args.get("status", "all")
    date_filter = request.args.get("date", "")
    
    query = Booking.query.filter_by(business_id=business.id)
    
    if status_filter and status_filter != "all":
        query = query.filter_by(status=status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            query = query.filter(Booking.booking_date == filter_date)
        except ValueError:
            pass
    
    bookings = query.order_by(Booking.booking_date.desc(), Booking.booking_time.desc()).all()
    return render_template("dashboard/bookings.html", bookings=bookings, business=business, 
                         status_filter=status_filter, date_filter=date_filter)

@dashboard_bp.route("/bookings/<int:booking_id>", methods=["GET", "POST"])
@login_required
def booking_detail(booking_id):
    business = get_user_business()
    if not business:
        return redirect(url_for("dashboard.create_business"))
    
    booking = Booking.query.filter_by(id=booking_id, business_id=business.id).first_or_404()
    form = BookingStatusForm(obj=booking)
    
    if form.validate_on_submit():
        booking.status = form.status.data
        db.session.commit()
        flash("Booking status updated!", "success")
        return redirect(url_for("dashboard.bookings"))
    
    return render_template("dashboard/booking_detail.html", booking=booking, form=form, business=business)

@dashboard_bp.route("/bookings/<int:booking_id>/confirm", methods=["POST"])
@login_required
def confirm_booking(booking_id):
    business = get_user_business()
    if not business:
        abort(404)
    
    booking = Booking.query.filter_by(id=booking_id, business_id=business.id).first_or_404()
    booking.status = "confirmed"
    db.session.commit()
    flash("Booking confirmed!", "success")
    return redirect(url_for("dashboard.bookings"))

@dashboard_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    business = get_user_business()
    if not business:
        abort(404)
    
    booking = Booking.query.filter_by(id=booking_id, business_id=business.id).first_or_404()
    booking.status = "cancelled"
    db.session.commit()
    flash("Booking cancelled.", "info")
    return redirect(url_for("dashboard.bookings"))
