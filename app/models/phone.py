from datetime import datetime
from app import db


class Phone(db.Model):
    __tablename__ = 'phones'

    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False, index=True)
    model = db.Column(db.String(100), nullable=False, index=True)
    release_year = db.Column(db.Integer)
    screen_size = db.Column(db.Float)  # in inches
    battery_capacity = db.Column(db.Integer)  # in mAh
    waterproof_rating = db.Column(db.String(20))  # e.g., IP68
    has_wireless_charging = db.Column(db.Boolean, default=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=True)
    imei = db.Column(db.String(15), unique=True, nullable=True) # IMEI is typically 15 digits
    storage_gb = db.Column(db.Integer, nullable=True) # Added from seed_data.py
    color = db.Column(db.String(50), nullable=True) # Added from seed_data.py
    price = db.Column(db.Float, nullable=True) # Added from seed_data.py
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # Deleting a Phone should delete its Issues and their dependent Repairs (delete-orphan)
    issues = db.relationship('Issue', backref='phone', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Phone {self.brand} {self.model}>'
