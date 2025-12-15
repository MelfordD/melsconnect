from datetime import datetime, date, time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    businesses = db.relationship("Business", back_populates="owner", lazy="dynamic")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Business(db.Model):
    __tablename__ = "businesses"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    owner = db.relationship("User", back_populates="businesses")
    services = db.relationship("Service", back_populates="business", lazy="dynamic", cascade="all, delete-orphan")
    working_hours = db.relationship("WorkingHour", back_populates="business", lazy="dynamic", cascade="all, delete-orphan")
    bookings = db.relationship("Booking", back_populates="business", lazy="dynamic", cascade="all, delete-orphan")
    
    def generate_slug(self):
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        while Business.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug

class Service(db.Model):
    __tablename__ = "services"
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    business = db.relationship("Business", back_populates="services")
    bookings = db.relationship("Booking", back_populates="service", lazy="dynamic")

class WorkingHour(db.Model):
    __tablename__ = "working_hours"
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    open_time = db.Column(db.Time, nullable=False)
    close_time = db.Column(db.Time, nullable=False)
    is_closed = db.Column(db.Boolean, default=False)
    
    business = db.relationship("Business", back_populates="working_hours")
    
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    @property
    def day_name(self):
        return self.DAY_NAMES[self.day_of_week]

class Booking(db.Model):
    __tablename__ = "bookings"
    
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey("businesses.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120))
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default="pending")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    business = db.relationship("Business", back_populates="bookings")
    service = db.relationship("Service", back_populates="bookings")
    
    STATUS_CHOICES = ["pending", "confirmed", "cancelled", "completed"]
    
    @property
    def end_time(self):
        from datetime import datetime, timedelta
        start_dt = datetime.combine(self.booking_date, self.booking_time)
        end_dt = start_dt + timedelta(minutes=self.service.duration_minutes)
        return end_dt.time()
