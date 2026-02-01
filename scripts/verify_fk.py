import os
import sys
# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app, db
import sqlalchemy as sa

app = create_app('development')
with app.app_context():
    insp = sa.inspect(db.engine)
    print('repairs foreign keys:')
    for fk in insp.get_foreign_keys('repairs'):
        print(' ', fk)
    print('\nrules foreign keys:')
    for fk in insp.get_foreign_keys('rules'):
        print(' ', fk)
