import os
from app import create_app, db
from app.models.user import User
from app.models.role import Role, Permission
from app.models.phone import Phone
from app.models.issue import Symptom, Issue # Import Issue and Symptom for cleanup
from app.models.repair import Repair, RepairRequest
from app.models.rule import Rule # Import Rule for cleanup
from app.models.associations import role_permissions, issue_symptoms # Import issue_symptoms for cleanup
from app.seeding.standardize_data import run_standardize
from app.seeding.seed_data import seed_all_data # Import seed_all_data

def clear_all_data():
    """Clears all data from the database in the correct dependency order."""
    print("Clearing all existing data...")
    # Clear tables dependent on others first
    db.session.query(Rule).delete()
    db.session.query(RepairRequest).delete() # RepairRequest depends on User
    db.session.query(Repair).delete() # Repair depends on Issue
    db.session.execute(issue_symptoms.delete()) # Association table
    db.session.query(Issue).delete() # Issue depends on Phone and Symptom
    db.session.query(Symptom).delete()
    db.session.query(Phone).delete()

    # Clear authentication and authorization tables
    db.session.execute(role_permissions.delete())
    db.session.query(User).delete() # User depends on Role
    db.session.query(Role).delete() # Role depends on nothing listed here
    db.session.query(Permission).delete() # Permission depends on nothing listed here
    
    db.session.commit()
    print("All existing data cleared.")

def seed_essentials():
    """Seed the database with essential data like roles, permissions, and admin user."""
    print("Seeding essential data (roles, permissions, admin user)...")

    # Create roles
    admin_role = Role(name='admin', description='Administrator')
    tech_role = Role(name='technician', description='Technician')
    user_role = Role(name='user', description='Regular User')
    db.session.add_all([admin_role, tech_role, user_role])
    db.session.commit()

    # Create permissions
    perms = [
        Permission(name='admin_access', description='Access admin panel'),
        Permission(name='manage_users', description='Manage users'),
        Permission(name='manage_rules', description='Manage expert system rules'),
        Permission(name='view_all_requests', description='View all repair requests')
    ]
    db.session.add_all(perms)
    db.session.commit()

    # Assign permissions to roles
    admin_role.permissions = perms
    tech_role.permissions.append(Permission.query.filter_by(name='view_all_requests').first())
    db.session.commit()

    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@phonerepair.com', full_name='System Admin')
        admin.set_password('admin123')
        admin.role = admin_role
        db.session.add(admin)
        db.session.commit()
        print("Admin user created - username: admin, password: admin123")
    
    # Do NOT delete or add Phone records here. This is handled by seed_all_data.
    print("Essential data (roles, permissions, admin user) seeded successfully!")


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    with app.app_context():
        # Clear all data before seeding
        clear_all_data()

        # Seed essential data first
        seed_essentials()
        
        # Now, seed the main data (phones, symptoms, issues, repairs, rules)
        print("Seeding all data (phones, symptoms, issues, repairs, rules)...")
        seed_all_data() # Call the comprehensive seed function
        
        # Finally, run standardization if needed
        run_standardize()
        
        print("Seed script finished.")
