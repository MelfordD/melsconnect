from app import app
from extensions import db
from models import User

def create_admin():
    with app.app_context():
        admin = User.query.filter_by(email="admin@melsconnect.com").first()
        if not admin:
            admin = User(
                email="admin@melsconnect.com",
                first_name="Admin",
                last_name="User",
                is_admin=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            print("Email: admin@melsconnect.com")
            print("Password: admin123")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    create_admin()
