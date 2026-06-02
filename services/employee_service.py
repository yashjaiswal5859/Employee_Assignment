from repositories.employee_repository import EmployeeRepository
from datetime import datetime
from typing import Dict, Any, List

class EmployeeService:
    """Service layer - Contains business logic for employees"""
    
    @staticmethod
    def validate_employee_data(name: str, email: str, department: str) -> None:
        """Validate employee data"""
        if not name or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        
        if not email or '@' not in email or '.' not in email.split('@')[1]:
            raise ValueError("Invalid email format")
        
        if not department or len(department.strip()) < 2:
            raise ValueError("Department must be at least 2 characters long")
    
    @staticmethod
    def create_employee(name: str, email: str, department: str, date_joined: str) -> Dict[str, Any]:
        """Business logic for creating an employee"""
        # Validation
        EmployeeService.validate_employee_data(name, email, department)
        
        # Check if email already exists
        if EmployeeRepository.get_employee_by_email(email):
            raise ValueError(f"Employee with email {email} already exists")
        
        # Parse and validate date
        try:
            joined_date = datetime.strptime(date_joined, '%Y-%m-%d').date()
            if joined_date > datetime.now().date():
                raise ValueError("Date joined cannot be in the future")
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError("Date must be in format YYYY-MM-DD")
            raise
        
        # Create employee
        employee = EmployeeRepository.create_employee(name, email, department, joined_date)
        return employee.to_dict()
    
    @staticmethod
    def get_employee(employee_id: int) -> Dict[str, Any]:
        """Business logic for fetching an employee"""
        if not isinstance(employee_id, int) or employee_id <= 0:
            raise ValueError("Invalid employee ID")
        
        employee = EmployeeRepository.get_employee_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        return employee.to_dict()
    
    @staticmethod
    def get_all_employees() -> List[Dict[str, Any]]:
        """Business logic for fetching all employees"""
        employees = EmployeeRepository.get_all_employees()
        return [employee.to_dict() for employee in employees]
    
    @staticmethod
    def update_employee(employee_id: int, name: str = None, email: str = None, 
                       department: str = None, date_joined: str = None) -> Dict[str, Any]:
        """Business logic for updating an employee"""
        if not isinstance(employee_id, int) or employee_id <= 0:
            raise ValueError("Invalid employee ID")
        
        # Check if employee exists
        employee = EmployeeRepository.get_employee_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        # Prepare update data
        update_data = {}
        
        if name is not None:
            if len(name.strip()) < 2:
                raise ValueError("Name must be at least 2 characters long")
            update_data['name'] = name
        
        if email is not None:
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValueError("Invalid email format")
            # Check if email is already used by another employee
            if EmployeeRepository.employee_exists_by_email(email, exclude_id=employee_id):
                raise ValueError(f"Email {email} is already in use")
            update_data['email'] = email
        
        if department is not None:
            if len(department.strip()) < 2:
                raise ValueError("Department must be at least 2 characters long")
            update_data['department'] = department
        
        if date_joined is not None:
            try:
                joined_date = datetime.strptime(date_joined, '%Y-%m-%d').date()
                if joined_date > datetime.now().date():
                    raise ValueError("Date joined cannot be in the future")
                update_data['date_joined'] = joined_date
            except ValueError as e:
                if "does not match format" in str(e):
                    raise ValueError("Date must be in format YYYY-MM-DD")
                raise
        
        # Update employee
        updated_employee = EmployeeRepository.update_employee(employee_id, **update_data)
        return updated_employee.to_dict()
    
    @staticmethod
    def delete_employee(employee_id: int) -> Dict[str, str]:
        """Business logic for deleting an employee"""
        if not isinstance(employee_id, int) or employee_id <= 0:
            raise ValueError("Invalid employee ID")
        
        # Check if employee exists
        if not EmployeeRepository.get_employee_by_id(employee_id):
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        # Delete employee
        EmployeeRepository.delete_employee(employee_id)
        return {"message": f"Employee with ID {employee_id} deleted successfully"}
