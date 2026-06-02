import pytest
from repositories.employee_repository import EmployeeRepository
from models import db, Employee


class TestEmployeeRepository:
    """Test cases for Employee Repository layer"""

    def test_create_employee(self, app, sample_employee):
        """Test creating an employee in the database"""
        with app.app_context():
            employee = EmployeeRepository.create_employee(
                sample_employee['name'],
                sample_employee['email'],
                sample_employee['department'],
                sample_employee['date_joined']
            )

            assert employee.id is not None
            assert employee.name == sample_employee['name']
            assert employee.email == sample_employee['email']

    def test_get_employee_by_id(self, app, sample_employee):
        """Test retrieving employee by ID"""
        with app.app_context():
            created = EmployeeRepository.create_employee(
                sample_employee['name'],
                sample_employee['email'],
                sample_employee['department'],
                sample_employee['date_joined']
            )

            retrieved = EmployeeRepository.get_employee_by_id(created.id)

            assert retrieved is not None
            assert retrieved.id == created.id
            assert retrieved.name == sample_employee['name']

    def test_get_employee_by_email(self, app, sample_employee):
        """Test retrieving employee by email"""
        with app.app_context():
            EmployeeRepository.create_employee(
                sample_employee['name'],
                sample_employee['email'],
                sample_employee['department'],
                sample_employee['date_joined']
            )

            retrieved = EmployeeRepository.get_employee_by_email(sample_employee['email'])

            assert retrieved is not None
            assert retrieved.email == sample_employee['email']

    def test_get_all_employees(self, app, sample_employee):
        """Test retrieving all employees"""
        with app.app_context():
            EmployeeRepository.create_employee(
                sample_employee['name'],
                sample_employee['email'],
                sample_employee['department'],
                sample_employee['date_joined']
            )

            employees = EmployeeRepository.get_all_employees()

            assert len(employees) == 1
            assert employees[0].name == sample_employee['name']

    def test_update_employee(self, app, sample_employee):
        """Test updating an employee"""
        with app.app_context():
            created = EmployeeRepository.create_employee(
                sample_employee['name'],
                sample_employee['email'],
                sample_employee['department'],
                sample_employee['date_joined']
            )

            updated = EmployeeRepository.update_employee(
                created.id,
                name="Updated Name"
            )

            assert updated.name == "Updated Name"
            assert updated.email == sample_employee['email']

    def test_delete_employee(self, app, sample_employee):
        """Test deleting an employee"""
        with app.app_context():
            created = EmployeeRepository.create_employee(
                sample_employee['name'],
                sample_employee['email'],
                sample_employee['department'],
                sample_employee['date_joined']
            )

            success = EmployeeRepository.delete_employee(created.id)

            assert success is True
            assert EmployeeRepository.get_employee_by_id(created.id) is None

    def test_employee_exists_by_email(self, app, sample_employee):
        """Test checking if employee exists by email"""
        with app.app_context():
            EmployeeRepository.create_employee(
                sample_employee['name'],
                sample_employee['email'],
                sample_employee['department'],
                sample_employee['date_joined']
            )

            exists = EmployeeRepository.employee_exists_by_email(sample_employee['email'])
            assert exists is True

            not_exists = EmployeeRepository.employee_exists_by_email('nonexistent@example.com')
            assert not_exists is False
