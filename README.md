import os
from app import create_app, db
from app.models.user import User
from app.models.role import Role

# Ensure the Flask app is created

app = create_app()

with app.app_context():
username = "admin"
password = "admin123"
email = "admin@example.com" # Default email, can be changed

    # Find the 'Admin' role
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        print("Admin role not found. Please ensure roles are seeded (e.g., run migrations).")
        # Attempt to create Admin role if not found, though migrations are preferred
        admin_role = Role(name='Admin', description='Administrator role with full access')
        db.session.add(admin_role)
        db.session.commit()
        print("Admin role created as it was missing.")

    # Check if admin user already exists
    admin_user = User.query.filter_by(username=username).first()
    if admin_user:
        print(f"User '{username}' already exists. Updating password if changed.")
        admin_user.set_password(password)
        admin_user.email = email
        admin_user.role = admin_role
        db.session.commit()
        print(f"User '{username}' password and role updated.")
    else:
        # Create new admin user
        new_admin = User(username=username, email=email, role=admin_role)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
