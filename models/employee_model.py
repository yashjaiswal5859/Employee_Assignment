import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    date_joined = db.Column(db.Date, nullable=False, default=date.today)

    def to_dict(self):
        return {
            'id': str(self.id) if self.id else None,
            'name': self.name,
            'email': self.email,
            'department': self.department,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None
        }

    def __repr__(self):
        return f'<Employee {self.name}>'
