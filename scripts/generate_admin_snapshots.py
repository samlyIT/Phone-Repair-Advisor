"""Generate HTML snapshots of admin pages (issues and manage_rules).
This script seeds the DB, creates an admin user, logs in via test client,
fetches admin pages, and writes HTML files to docs/screenshots/.
"""
import os
import sys
# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app, db
from app.models.role import Role
from app.models.user import User
from app.seeding.seed_data import seed_all_data

OUT_DIR = os.path.join(os.getcwd(), 'docs', 'screenshots')
os.makedirs(OUT_DIR, exist_ok=True)

# Allow CI to override which Flask config to use (e.g. 'testing' for sqlite)
config_name = os.getenv('SNAPSHOT_CONFIG') or os.getenv('FLASK_ENV') or 'default'
print(f"Using app config: {config_name}")
app = create_app(config_name)
with app.app_context():
    # When using the testing config in CI, create tables since migrations may not run against an in-memory DB
    if config_name == 'testing':
        print('Testing config detected — creating database tables with db.create_all()')
        db.create_all()
    print("Inserting roles and admin user...")
    Role.insert_roles()

    admin_role = Role.query.filter_by(name='Admin').first()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', full_name='Admin User')
        admin.set_password('password')
        if admin_role:
            admin.role = admin_role
        db.session.add(admin)
        db.session.commit()
        print('Admin user created: admin / password')
    else:
        # Ensure we know the admin password for automated login
        admin.set_password('password')
        if admin_role:
            admin.role = admin_role
        db.session.add(admin)
        db.session.commit()
        print('Admin user ensured and password set: admin / password')

    print('Refreshing seed data...')
    # Clear and reseed via existing script logic
    from app.models.issue import Symptom, Issue
    from app.models.repair import Repair
    from app.models.rule import Rule
    from app.models.associations import issue_symptoms

    db.session.query(Rule).delete()
    db.session.query(Repair).delete()
    db.session.execute(issue_symptoms.delete())
    db.session.query(Issue).delete()
    db.session.query(Symptom).delete()
    db.session.commit()

    seed_all_data()

    # Use test client to log in and fetch admin pages
    client = app.test_client()
    login_data = {'username': 'admin', 'password': 'password'}
    resp = client.post('/auth/login', data=login_data, follow_redirects=True)
    if resp.status_code != 200:
        print('Login failed, status:', resp.status_code)

    # Fetch pages
    pages = {
        'issues.html': '/admin/issues',
        'manage_rules.html': '/admin/manage_rules'
    }
    for fname, path in pages.items():
        print('Fetching', path)
        r = client.get(path)
        if r.status_code == 200:
            out_path = os.path.join(OUT_DIR, fname)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(r.get_data(as_text=True))
            print('Saved', out_path)
        else:
            print('Failed to fetch', path, 'status', r.status_code)

    print('Snapshot generation complete.')
