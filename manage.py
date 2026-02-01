import os
from app import create_app
from app.extensions import db, migrate
from app.models.user import User
from app.models.role import Role, Permission
from app.models.phone import Phone # Added for clearing
from app.models.issue import Issue, Symptom # Added for clearing
from app.models.repair import Repair, RepairRequest # Added for clearing
from app.models.rule import Rule # Added for clearing
from app.models.associations import issue_symptoms, role_permissions # Added for clearing
from app.seeding.seed_data import seed_all_data

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
# The migrate object is now initialized in app.extensions, 
# so we don't need to instantiate it again here.

@app.cli.command()
def seed_db():
    """Seed the database with initial data using comprehensive seeding function"""
    print("Clearing existing data...")
    # Clear data in reverse order of dependency
    db.session.query(Rule).delete()
    db.session.query(RepairRequest).delete() # Clear RepairRequest before Repair
    db.session.query(Repair).delete()
    db.session.execute(issue_symptoms.delete()) # Clear association table
    db.session.query(Issue).delete()
    db.session.query(Symptom).delete()
    db.session.query(Phone).delete()
    db.session.execute(role_permissions.delete()) # Clear association table
    db.session.query(User).delete()
    db.session.query(Role).delete()
    db.session.query(Permission).delete()
    db.session.commit()
    print("Existing data cleared.")

    print("Seeding roles and admin user...")
    # Create roles
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrator')
        db.session.add(admin_role)
    
    tech_role = Role.query.filter_by(name='technician').first()
    if not tech_role:
        tech_role = Role(name='technician', description='Technician')
        db.session.add(tech_role)

    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Regular User')
        db.session.add(user_role)
    
    db.session.commit() # Commit roles to get their IDs
    
    # Create permissions
    perms_data = [
        {'name': 'admin_access', 'description': 'Access admin panel'},
        {'name': 'manage_users', 'description': 'Manage users'},
        {'name': 'manage_rules', 'description': 'Manage expert system rules'},
        {'name': 'view_all_requests', 'description': 'View all repair requests'}
    ]
    
    for perm_info in perms_data:
        perm = Permission.query.filter_by(name=perm_info['name']).first()
        if not perm:
            perm = Permission(**perm_info)
            db.session.add(perm)
    db.session.commit() # Commit permissions to get their IDs

    # Assign permissions to roles
    admin_perms = [Permission.query.filter_by(name=p['name']).first() for p in perms_data]
    if admin_role and not admin_role.permissions:
        admin_role.permissions = admin_perms
    
    tech_view_requests_perm = Permission.query.filter_by(name='view_all_requests').first()
    if tech_role and tech_view_requests_perm and not tech_role.permissions:
        tech_role.permissions = [tech_view_requests_perm]
    
    db.session.commit()
    
    # Create admin user
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@phonerepair.com', full_name='System Admin')
        admin_user.set_password('admin123')
        admin_user.role = admin_role
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created - username: admin, password: admin123")
    else:
        print("Admin user already exists.")

    print("Seeding comprehensive sample data...")
    seed_all_data()
    print("Database seeding complete!")