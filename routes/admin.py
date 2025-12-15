from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from app import db
from models import User, Business, Service, WorkingHour, Booking
from forms import AdminBusinessForm, AdminUserForm

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    total_businesses = Business.query.count()
    active_businesses = Business.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status="pending").count()
    
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    return render_template("admin/dashboard.html",
                         total_businesses=total_businesses,
                         active_businesses=active_businesses,
                         total_users=total_users,
                         total_bookings=total_bookings,
                         pending_bookings=pending_bookings,
                         recent_bookings=recent_bookings)

@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/users/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_user():
    form = AdminUserForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash("Email already exists.", "error")
        else:
            user = User(
                email=form.email.data.lower(),
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                is_admin=form.is_admin.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("User created successfully!", "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, title="Add User")

@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing and existing.id != user.id:
            flash("Email already exists.", "error")
        else:
            user.email = form.email.data.lower()
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.is_admin = form.is_admin.data
            if form.password.data:
                user.set_password(form.password.data)
            db.session.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, user=user, title="Edit User")

@admin_bp.route("/businesses")
@login_required
@admin_required
def businesses():
    businesses = Business.query.order_by(Business.created_at.desc()).all()
    return render_template("admin/businesses.html", businesses=businesses)

@admin_bp.route("/businesses/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_business():
    form = AdminBusinessForm()
    form.owner_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.order_by(User.first_name).all()]
    
    if form.validate_on_submit():
        business = Business(
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            description=form.description.data,
            owner_id=form.owner_id.data,
            is_active=form.is_active.data
        )
        business.generate_slug()
        db.session.add(business)
        db.session.commit()
        
        from datetime import time
        for day in range(7):
            wh = WorkingHour(
                business_id=business.id,
                day_of_week=day,
                open_time=time(9, 0),
                close_time=time(17, 0),
                is_closed=(day >= 5)
            )
            db.session.add(wh)
        db.session.commit()
        
        flash("Business created successfully!", "success")
        return redirect(url_for("admin.businesses"))
    return render_template("admin/business_form.html", form=form, title="Add Business")

@admin_bp.route("/businesses/<int:business_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_business(business_id):
    business = Business.query.get_or_404(business_id)
    form = AdminBusinessForm(obj=business)
    form.owner_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.order_by(User.first_name).all()]
    
    if form.validate_on_submit():
        business.name = form.name.data
        business.phone = form.phone.data
        business.address = form.address.data
        business.description = form.description.data
        business.owner_id = form.owner_id.data
        business.is_active = form.is_active.data
        db.session.commit()
        flash("Business updated successfully!", "success")
        return redirect(url_for("admin.businesses"))
    return render_template("admin/business_form.html", form=form, business=business, title="Edit Business")

@admin_bp.route("/businesses/<int:business_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_business(business_id):
    business = Business.query.get_or_404(business_id)
    business.is_active = not business.is_active
    db.session.commit()
    status = "activated" if business.is_active else "deactivated"
    flash(f"Business {status} successfully!", "success")
    return redirect(url_for("admin.businesses"))

@admin_bp.route("/bookings")
@login_required
@admin_required
def bookings():
    status_filter = request.args.get("status", "all")
    business_filter = request.args.get("business", "all")
    
    query = Booking.query
    
    if status_filter and status_filter != "all":
        query = query.filter_by(status=status_filter)
    
    if business_filter and business_filter != "all":
        query = query.filter_by(business_id=int(business_filter))
    
    bookings = query.order_by(Booking.created_at.desc()).all()
    businesses = Business.query.order_by(Business.name).all()
    
    return render_template("admin/bookings.html", bookings=bookings, businesses=businesses,
                         status_filter=status_filter, business_filter=business_filter)
