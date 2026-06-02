from flask import Blueprint, request, jsonify
from services.employee_service import EmployeeService

employee_bp = Blueprint('employees', __name__, url_prefix='/employees')


@employee_bp.route('', methods=['POST'])
def create_employee():
    """Add a new employee"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = ['name', 'email', 'department', 'date_joined']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        employee = EmployeeService.create_employee(
            name=data['name'],
            email=data['email'],
            department=data['department'],
            date_joined=data['date_joined']
        )

        return jsonify(employee), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@employee_bp.route('', methods=['GET'])
def get_all_employees():
    """Retrieve a list of all employees"""
    try:
        employees = EmployeeService.get_all_employees()
        return jsonify(employees), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@employee_bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Retrieve details of a specific employee"""
    try:
        employee = EmployeeService.get_employee(employee_id)
        return jsonify(employee), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@employee_bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Update an existing employee's information"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        employee = EmployeeService.update_employee(
            employee_id=employee_id,
            name=data.get('name'),
            email=data.get('email'),
            department=data.get('department'),
            date_joined=data.get('date_joined')
        )

        return jsonify(employee), 200

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            return jsonify({"error": error_msg}), 404
        return jsonify({"error": error_msg}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@employee_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Remove an employee from the system"""
    try:
        result = EmployeeService.delete_employee(employee_id)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
