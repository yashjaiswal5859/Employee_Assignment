from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Employee(db.Model):
    """Employee model for the database"""
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    date_joined = db.Column(db.Date, nullable=False, default=date.today)

    def to_dict(self):
        """Convert employee object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None
        }

    def __repr__(self):
        return f'<Employee {self.name}>'
