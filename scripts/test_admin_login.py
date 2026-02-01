import os
import sys
# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app, db
from app.models.user import User
from app.models.role import Role

app = create_app('development')
with app.app_context():
    # Ensure roles exist and admin has known password
    r = Role.query.filter_by(name='admin').first()
    if not r:
        r = Role(name='admin', description='Administrator')
        db.session.add(r)
        db.session.commit()

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@phonerepair.com', full_name='System Admin')
        admin.set_password('admin123')
        admin.role = r
        db.session.add(admin)
        db.session.commit()
        print('Created admin with password admin123')
    else:
        admin.set_password('admin123')
        admin.role = r
        db.session.add(admin)
        db.session.commit()
        print('Reset admin password to admin123')

    client = app.test_client()
    resp = client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    print('Login status:', resp.status_code)
    if resp.status_code == 200:
        print('Response body (first 400 chars):')
        print(resp.get_data(as_text=True)[:400])
    else:
        print('Login failed — response code', resp.status_code)
        print(resp.get_data(as_text=True)[:400])