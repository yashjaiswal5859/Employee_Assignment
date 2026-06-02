import pytest
from services.employee_service import EmployeeService


class TestEmployeeService:
    """Test cases for Employee Service layer"""

    def test_create_employee_success(self, app, sample_employee):
        """Test successful employee creation"""
        with app.app_context():
            employee = EmployeeService.create_employee(**sample_employee)

            assert employee['name'] == sample_employee['name']
            assert employee['email'] == sample_employee['email']
            assert employee['department'] == sample_employee['department']
            assert 'id' in employee

    def test_create_employee_invalid_name(self, app, sample_employee):
        """Test employee creation with invalid name"""
        with app.app_context():
            sample_employee['name'] = 'A'

            with pytest.raises(ValueError, match="Name must be at least 2 characters"):
                EmployeeService.create_employee(**sample_employee)

    def test_create_employee_invalid_email(self, app, sample_employee):
        """Test employee creation with invalid email"""
        with app.app_context():
            sample_employee['email'] = 'invalid-email'

            with pytest.raises(ValueError, match="Invalid email format"):
                EmployeeService.create_employee(**sample_employee)

    def test_create_employee_invalid_department(self, app, sample_employee):
        """Test employee creation with invalid department"""
        with app.app_context():
            sample_employee['department'] = 'A'

            with pytest.raises(ValueError, match="Department must be at least 2 characters"):
                EmployeeService.create_employee(**sample_employee)

    def test_create_employee_invalid_date_format(self, app, sample_employee):
        """Test employee creation with invalid date format"""
        with app.app_context():
            sample_employee['date_joined'] = '01-15-2024'

            with pytest.raises(ValueError, match="Date must be in format YYYY-MM-DD"):
                EmployeeService.create_employee(**sample_employee)

    def test_create_employee_future_date(self, app, sample_employee):
        """Test employee creation with future date"""
        with app.app_context():
            sample_employee['date_joined'] = '2099-01-15'

            with pytest.raises(ValueError, match="Date joined cannot be in the future"):
                EmployeeService.create_employee(**sample_employee)

    def test_create_employee_duplicate_email(self, app, sample_employee):
        """Test employee creation with duplicate email"""
        with app.app_context():
            EmployeeService.create_employee(**sample_employee)

            with pytest.raises(ValueError, match="already exists"):
                EmployeeService.create_employee(**sample_employee)

    def test_get_employee_success(self, app, sample_employee):
        """Test successful employee retrieval"""
        with app.app_context():
            created = EmployeeService.create_employee(**sample_employee)
            retrieved = EmployeeService.get_employee(created['id'])

            assert retrieved['name'] == sample_employee['name']
            assert retrieved['email'] == sample_employee['email']

    def test_get_employee_not_found(self, app):
        """Test getting non-existent employee"""
        with app.app_context():
            with pytest.raises(ValueError, match="not found"):
                EmployeeService.get_employee(999)

    def test_get_all_employees(self, app, sample_employee):
        """Test getting all employees"""
        with app.app_context():
            EmployeeService.create_employee(**sample_employee)

            employees = EmployeeService.get_all_employees()
            assert len(employees) == 1
            assert employees[0]['name'] == sample_employee['name']

    def test_update_employee_success(self, app, sample_employee):
        """Test successful employee update"""
        with app.app_context():
            created = EmployeeService.create_employee(**sample_employee)

            updated = EmployeeService.update_employee(
                created['id'],
                name="Jane Doe",
                department="Management"
            )

            assert updated['name'] == "Jane Doe"
            assert updated['department'] == "Management"
            assert updated['email'] == sample_employee['email']

    def test_update_employee_not_found(self, app):
        """Test updating non-existent employee"""
        with app.app_context():
            with pytest.raises(ValueError, match="not found"):
                EmployeeService.update_employee(999, name="Test")

    def test_delete_employee_success(self, app, sample_employee):
        """Test successful employee deletion"""
        with app.app_context():
            created = EmployeeService.create_employee(**sample_employee)

            result = EmployeeService.delete_employee(created['id'])

            assert "deleted successfully" in result['message']

            with pytest.raises(ValueError):
                EmployeeService.get_employee(created['id'])

    def test_delete_employee_not_found(self, app):
        """Test deleting non-existent employee"""
        with app.app_context():
            with pytest.raises(ValueError, match="not found"):
                EmployeeService.delete_employee(999)
