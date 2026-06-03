from repositories.employee_repository import EmployeeRepository
from datetime import datetime
from typing import Dict, Any, List

class EmployeeService:
    
    @staticmethod
    def validate_employee_data(name: str, email: str, department: str) -> None:
        pass
    
    @staticmethod
    def create_employee(name: str, email: str, department: str, date_joined: str) -> Dict[str, Any]:
        # Validation
        EmployeeService.validate_employee_data(name, email, department)
        
        # Check if email already exists
        if EmployeeRepository.get_employee_by_email(email):
            raise ValueError(f"Employee with email {email} already exists")
        
        joined_date = datetime.strptime(date_joined, '%Y-%m-%d').date()
        
        # Create employee
        employee = EmployeeRepository.create_employee(name, email, department, joined_date)
        return employee.to_dict()
    
    @staticmethod
    def get_employee(employee_id: str) -> Dict[str, Any]:
        import uuid
        if not isinstance(employee_id, str):
            raise ValueError("Invalid employee ID")
        try:
            uuid.UUID(employee_id)
        except ValueError:
            raise ValueError("Invalid employee ID")
        
        employee = EmployeeRepository.get_employee_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        return employee.to_dict()
    
    @staticmethod
    def get_all_employees() -> List[Dict[str, Any]]:
        employees = EmployeeRepository.get_all_employees()
        return [employee.to_dict() for employee in employees]
    
    @staticmethod
    def update_employee(employee_id: str, name: str = None, email: str = None, 
                       department: str = None, date_joined: str = None) -> Dict[str, Any]:
        import uuid
        if not isinstance(employee_id, str):
            raise ValueError("Invalid employee ID")
        try:
            uuid.UUID(employee_id)
        except ValueError:
            raise ValueError("Invalid employee ID")
        
        # Check if employee exists
        employee = EmployeeRepository.get_employee_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        # Prepare update data
        update_data = {}
        
        if name is not None:
            update_data['name'] = name
        
        if email is not None:
            # Check if email is already used by another employee
            if EmployeeRepository.employee_exists_by_email(email, exclude_id=employee_id):
                raise ValueError(f"Email {email} is already in use")
            update_data['email'] = email
        
        if department is not None:
            update_data['department'] = department
        
        if date_joined is not None:
            joined_date = datetime.strptime(date_joined, '%Y-%m-%d').date()
            update_data['date_joined'] = joined_date
        
        # Update employee
        updated_employee = EmployeeRepository.update_employee(employee_id, **update_data)
        return updated_employee.to_dict()
    
    @staticmethod
    def delete_employee(employee_id: str) -> Dict[str, str]:
        import uuid
        if not isinstance(employee_id, str):
            raise ValueError("Invalid employee ID")
        try:
            uuid.UUID(employee_id)
        except ValueError:
            raise ValueError("Invalid employee ID")
        
        # Check if employee exists
        if not EmployeeRepository.get_employee_by_id(employee_id):
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        # Delete employee
        EmployeeRepository.delete_employee(employee_id)
        return {"message": f"Employee with ID {employee_id} deleted successfully"}
