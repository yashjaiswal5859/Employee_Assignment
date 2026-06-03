from flask import Blueprint, request, jsonify
from services.employee_service import EmployeeService
from dtos.request.employee_request import CreateEmployeeRequestDTO, UpdateEmployeeRequestDTO
from dtos.response.employee_response import (
    CreateEmployeeResponseDTO, UpdateEmployeeResponseDTO,
    GetEmployeeResponseDTO, GetAllEmployeesResponseDTO,
    DeleteEmployeeResponseDTO
)
from pydantic import ValidationError

employee_bp = Blueprint('employees', __name__, url_prefix='/employees')


@employee_bp.route('', methods=['POST'])
def create_employee():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        validated_data = CreateEmployeeRequestDTO(**data)

        employee = EmployeeService.create_employee(
            name=validated_data.name,
            email=validated_data.email,
            department=validated_data.department,
            date_joined=validated_data.date_joined.isoformat()
        )

        return jsonify(CreateEmployeeResponseDTO(**employee).model_dump(mode='json')), 201

    except ValidationError as e:
        safe_errors = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
        return jsonify({"error": "Validation Error", "details": safe_errors}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@employee_bp.route('', methods=['GET'])
def get_all_employees():
    try:
        employees = EmployeeService.get_all_employees()
        return jsonify([GetAllEmployeesResponseDTO(**e).model_dump(mode='json') for e in employees]), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@employee_bp.route('/<uuid:employee_id>', methods=['GET'])
def get_employee(employee_id):
    try:
        employee = EmployeeService.get_employee(str(employee_id))
        return jsonify(GetEmployeeResponseDTO(**employee).model_dump(mode='json')), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@employee_bp.route('/<uuid:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        validated_data = UpdateEmployeeRequestDTO(**data)

        employee = EmployeeService.update_employee(
            employee_id=str(employee_id),
            name=validated_data.name,
            email=validated_data.email,
            department=validated_data.department,
            date_joined=validated_data.date_joined.isoformat() if validated_data.date_joined else None
        )

        return jsonify(UpdateEmployeeResponseDTO(**employee).model_dump(mode='json')), 200

    except ValidationError as e:
        safe_errors = [{"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")} for err in e.errors()]
        return jsonify({"error": "Validation Error", "details": safe_errors}), 400
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            return jsonify({"error": error_msg}), 404
        return jsonify({"error": error_msg}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@employee_bp.route('/<uuid:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        result = EmployeeService.delete_employee(str(employee_id))
        return jsonify(DeleteEmployeeResponseDTO(**result).model_dump(mode='json')), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
