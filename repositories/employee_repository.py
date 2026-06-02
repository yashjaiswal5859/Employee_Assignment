from models import Employee, db
from typing import List, Optional

class EmployeeRepository:
    """Repository layer - Handles all database operations for employees"""
    
    @staticmethod
    def create_employee(name: str, email: str, department: str, date_joined) -> Employee:
        """Create and save a new employee to database"""
        employee = Employee(
            name=name,
            email=email,
            department=department,
            date_joined=date_joined
        )
        db.session.add(employee)
        db.session.commit()
        return employee
    
    @staticmethod
    def get_employee_by_id(employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        return Employee.query.get(employee_id)
    
    @staticmethod
    def get_employee_by_email(email: str) -> Optional[Employee]:
        """Get employee by email"""
        return Employee.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all_employees() -> List[Employee]:
        """Get all employees"""
        return Employee.query.all()
    
    @staticmethod
    def update_employee(employee_id: int, **kwargs) -> Optional[Employee]:
        """Update employee with given fields"""
        employee = Employee.query.get(employee_id)
        if not employee:
            return None
        
        for key, value in kwargs.items():
            if hasattr(employee, key) and key not in ['id', 'created_at']:
                setattr(employee, key, value)
        
        db.session.commit()
        return employee
    
    @staticmethod
    def delete_employee(employee_id: int) -> bool:
        """Delete employee by ID"""
        employee = Employee.query.get(employee_id)
        if not employee:
            return False
        
        db.session.delete(employee)
        db.session.commit()
        return True
    
    @staticmethod
    def employee_exists_by_email(email: str, exclude_id: int = None) -> bool:
        """Check if employee exists by email (optionally excluding a specific ID)"""
        query = Employee.query.filter_by(email=email)
        if exclude_id:
            query = query.filter(Employee.id != exclude_id)
        return query.first() is not None
