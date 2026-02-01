from datetime import datetime
from app import db
from app.models.associations import issue_symptoms


class Issue(db.Model):
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    phone_id = db.Column(db.Integer, db.ForeignKey('phones.id'))
    category = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=True) # Added code column
    description = db.Column(db.Text)
    severity = db.Column(db.String(20))  # Low, Medium, High, Critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    symptoms = db.relationship(
        'Symptom',
        secondary=issue_symptoms,
        backref='issues')
    # Cascade so that deleting an Issue removes its Repairs too
    repairs = db.relationship('Repair', backref='issue', lazy='select', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Issue {self.name}>'


class Symptom(db.Model):
    __tablename__ = 'symptoms'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    question = db.Column(db.String(255))  # Question to ask user

    def __repr__(self):
        return f'<Symptom {self.code}>'
