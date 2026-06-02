import pytest
import json


class TestEmployeeController:
    """Test cases for Employee Controller layer"""

    def test_create_employee_success(self, client, sample_employee):
        """Test successful employee creation via API"""
        response = client.post(
            '/employees',
            data=json.dumps(sample_employee),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == sample_employee['name']
        assert data['email'] == sample_employee['email']
        assert 'id' in data

    def test_create_employee_missing_fields(self, client):
        """Test creating employee with missing fields"""
        incomplete_data = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }

        response = client.post(
            '/employees',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_create_employee_invalid_data(self, client, sample_employee):
        """Test creating employee with invalid data"""
        sample_employee['name'] = 'A'

        response = client.post(
            '/employees',
            data=json.dumps(sample_employee),
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_get_all_employees(self, client, sample_employee):
        """Test getting all employees"""
        client.post(
            '/employees',
            data=json.dumps(sample_employee),
            content_type='application/json'
        )

        response = client.get('/employees')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_get_employee_by_id(self, client, sample_employee):
        """Test getting employee by ID"""
        create_response = client.post(
            '/employees',
            data=json.dumps(sample_employee),
            content_type='application/json'
        )
        created_data = json.loads(create_response.data)
        employee_id = created_data['id']

        response = client.get(f'/employees/{employee_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == employee_id
        assert data['name'] == sample_employee['name']

    def test_get_employee_not_found(self, client):
        """Test getting non-existent employee"""
        response = client.get('/employees/999')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_update_employee_success(self, client, sample_employee):
        """Test successful employee update"""
        create_response = client.post(
            '/employees',
            data=json.dumps(sample_employee),
            content_type='application/json'
        )
        created_data = json.loads(create_response.data)
        employee_id = created_data['id']

        update_data = {'name': 'Updated Name', 'department': 'Marketing'}
        response = client.put(
            f'/employees/{employee_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated Name'
        assert data['department'] == 'Marketing'

    def test_update_employee_not_found(self, client):
        """Test updating non-existent employee"""
        update_data = {'name': 'Updated Name'}

        response = client.put(
            '/employees/999',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 404

    def test_delete_employee_success(self, client, sample_employee):
        """Test successful employee deletion"""
        create_response = client.post(
            '/employees',
            data=json.dumps(sample_employee),
            content_type='application/json'
        )
        created_data = json.loads(create_response.data)
        employee_id = created_data['id']

        response = client.delete(f'/employees/{employee_id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'deleted successfully' in data['message']

    def test_delete_employee_not_found(self, client):
        """Test deleting non-existent employee"""
        response = client.delete('/employees/999')

        assert response.status_code == 404

    def test_home_endpoint(self, client):
        """Test home endpoint"""
        response = client.get('/')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'endpoints' in data
