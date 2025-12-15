from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, IntegerField, SelectField, DateField, TimeField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("This email is already registered.")

class BusinessForm(FlaskForm):
    name = StringField("Business Name", validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])

class ServiceForm(FlaskForm):
    name = StringField("Service Name", validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)])
    duration_minutes = IntegerField("Duration (minutes)", validators=[DataRequired(), NumberRange(min=5, max=480)])

class WorkingHourForm(FlaskForm):
    day_of_week = SelectField("Day", choices=[
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"),
        (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday")
    ], coerce=int)
    open_time = TimeField("Open Time", validators=[DataRequired()])
    close_time = TimeField("Close Time", validators=[DataRequired()])
    is_closed = BooleanField("Closed")

class BookingForm(FlaskForm):
    service_id = SelectField("Service", validators=[DataRequired()], coerce=int)
    booking_date = DateField("Date", validators=[DataRequired()])
    booking_time = SelectField("Time", validators=[DataRequired()])
    customer_name = StringField("Your Name", validators=[DataRequired(), Length(min=2, max=100)])
    customer_phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=20)])
    customer_email = StringField("Email (optional)", validators=[Optional(), Email()])
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=500)])

class BookingStatusForm(FlaskForm):
    status = SelectField("Status", choices=[
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed")
    ])

class AdminBusinessForm(FlaskForm):
    name = StringField("Business Name", validators=[DataRequired(), Length(min=2, max=100)])
    owner_id = SelectField("Owner", validators=[DataRequired()], coerce=int)
    phone = StringField("Phone Number", validators=[Optional(), Length(max=20)])
    address = StringField("Address", validators=[Optional(), Length(max=255)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    is_active = BooleanField("Active")

class AdminUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Password", validators=[Optional(), Length(min=6)])
    is_admin = BooleanField("Admin Access")
