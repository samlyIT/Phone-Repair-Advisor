# seed_db.py
import os
from app import create_app, db
from app.seeding.seed_data import seed_all_data

# Create a Flask app instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Push an application context
with app.app_context():
    print("Running database seeding...")
    # Clear existing data first (optional, but good for consistent seeding)
    from app.models.issue import Symptom, Issue
    from app.models.repair import Repair
    from app.models.rule import Rule
    from app.models.associations import issue_symptoms

    print("Clearing existing data...")
    # Clear data in reverse order of dependency
    db.session.query(Rule).delete()
    db.session.query(Repair).delete()
    db.session.execute(issue_symptoms.delete()) # Clear association table
    db.session.query(Issue).delete()
    db.session.query(Symptom).delete()
    db.session.commit()
    print("Existing data cleared.")

    seed_all_data()
    print("Database seeding complete.")
