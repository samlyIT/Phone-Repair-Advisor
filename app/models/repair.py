from datetime import datetime
from app import db
import json


class Repair(db.Model):
    __tablename__ = 'repairs'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(
        db.Integer,
        db.ForeignKey('issues.id'),
        nullable=False)
    solution = db.Column(db.Text, nullable=False)
    estimated_cost_min = db.Column(db.Float)
    estimated_cost_max = db.Column(db.Float)
    estimated_time_hours = db.Column(db.Float)
    difficulty = db.Column(db.String(20))  # Easy, Medium, Hard, Expert
    parts_needed = db.Column(db.Text)  # JSON or comma-separated
    tools_needed = db.Column(db.Text)
    warranty_affected = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)  # Higher = more recommended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Repair {self.id} for Issue {self.issue_id}>'


class RepairRequest(db.Model):
    __tablename__ = 'repair_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    phone_brand = db.Column(db.String(50))
    phone_model = db.Column(db.String(100))
    symptoms_json = db.Column(db.Text)  # JSON of selected symptoms
    diagnosed_issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'))
    recommended_repair_id = db.Column(db.Integer, db.ForeignKey('repairs.id'))
    # pending, diagnosed, completed
    status = db.Column(db.String(20), default='pending')
    diagnosis_json = db.Column(db.Text)  # JSON of diagnosis result
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    diagnosed_issue = db.relationship(
        'Issue', foreign_keys=[diagnosed_issue_id])
    recommended_repair = db.relationship(
        'Repair', foreign_keys=[recommended_repair_id])

    @property
    def diagnosis(self):
        if self.diagnosis_json:
            return json.loads(self.diagnosis_json)
        return None

    @diagnosis.setter
    def diagnosis(self, value):
        self.diagnosis_json = json.dumps(value)

    def __repr__(self):
        return f'<RepairRequest {self.id}>'
