
from app import db
from datetime import datetime


class Rule(db.Model):
    __tablename__ = 'rules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    conditions = db.Column(db.JSON, nullable=False)
    actions = db.Column(db.JSON, nullable=False)
    priority = db.Column(db.Integer, default=1)
    confidence = db.Column(db.Float, default=1.0)
    description = db.Column(db.Text, nullable=True, default='Expert rule for phone diagnosis')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Add foreign key to Repair (nullable) and ensure related Rules are removed when a Repair is removed
    repair_id = db.Column(db.Integer, db.ForeignKey('repairs.id', ondelete='SET NULL'), nullable=True)
    # Keep rules even if a referenced Repair is deleted; DB will set repair_id to NULL
    repair = db.relationship('Repair', backref=db.backref('rules'))

    def __repr__(self):
        return f'<Rule {self.name}>'
