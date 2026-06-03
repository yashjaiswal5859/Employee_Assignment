import logging
import uuid
from flask import Blueprint, request, jsonify
from services.employee_service import EmployeeService
from dtos.request.employee_request import (
    CreateEmployeeRequestDTO,
    UpdateEmployeeRequestDTO,
)
from dtos.response.employee_response import (
    CreateEmployeeResponseDTO,
    UpdateEmployeeResponseDTO,
    GetEmployeeResponseDTO,
    GetAllEmployeesResponseDTO,
    DeleteEmployeeResponseDTO,
)
from pydantic import ValidationError
from utils.constants import (
    APIError,
    STATUS_OK,
    STATUS_CREATED,
    STATUS_BAD_REQUEST,
    STATUS_INTERNAL_ERROR,
    ERR_BODY_REQUIRED,
    ERR_VALIDATION_FAILED,
    ERR_INTERNAL_SERVER,
)

employee_bp = Blueprint("employees", __name__, url_prefix="/employees")
logger = logging.getLogger(__name__)


@employee_bp.route("", methods=["POST"])
def create_employee():
    try:
        data = request.get_json()
        logger.info("POST /employees - Received payload: %s", data)

        if not data:
            logger.warning("POST /employees - Missing request body")
            return jsonify({"error": ERR_BODY_REQUIRED}), STATUS_BAD_REQUEST

        validated_data = CreateEmployeeRequestDTO(**data)

        employee = EmployeeService.create_employee(
            name=validated_data.name,
            email=validated_data.email,
            department=validated_data.department,
            date_joined=validated_data.date_joined.isoformat(),
        )

        logger.info(
            "POST /employees - Successfully created employee ID: %s", employee.get("id")
        )
        return jsonify(
            CreateEmployeeResponseDTO(**employee).model_dump(mode="json")
        ), STATUS_CREATED

    except ValidationError as e:
        safe_errors = [
            {"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")}
            for err in e.errors()
        ]
        logger.warning("POST /employees - Validation Error: %s", safe_errors)
        return jsonify(
            {"error": ERR_VALIDATION_FAILED, "details": safe_errors}
        ), STATUS_BAD_REQUEST
    except APIError as e:
        logger.warning("POST /employees - API Error: %s", e.message)
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        logger.exception("POST /employees - Unexpected error occurred")
        return jsonify({"error": ERR_INTERNAL_SERVER}), STATUS_INTERNAL_ERROR


@employee_bp.route("", methods=["GET"])
def get_all_employees():
    try:
        logger.info("GET /employees - Fetching all employees")
        employees = EmployeeService.get_all_employees()
        logger.info(
            "GET /employees - Successfully retrieved %d employees", len(employees)
        )
        return jsonify(
            [GetAllEmployeesResponseDTO(**e).model_dump(mode="json") for e in employees]
        ), STATUS_OK
    except Exception as e:
        logger.exception("GET /employees - Unexpected error occurred")
        return jsonify({"error": ERR_INTERNAL_SERVER}), STATUS_INTERNAL_ERROR


@employee_bp.route("/<string:employee_id>", methods=["GET"])
def get_employee(employee_id):
    try:
        logger.info("GET /employees/%s - Fetching employee details", employee_id)
        employee = EmployeeService.get_employee(employee_id)
        logger.info(
            "GET /employees/%s - Successfully retrieved employee details", employee_id
        )
        return jsonify(
            GetEmployeeResponseDTO(**employee).model_dump(mode="json")
        ), STATUS_OK
    except APIError as e:
        logger.warning("GET /employees/%s - API Error: %s", employee_id, e.message)
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        logger.exception("GET /employees/%s - Unexpected error occurred", employee_id)
        return jsonify({"error": ERR_INTERNAL_SERVER}), STATUS_INTERNAL_ERROR


@employee_bp.route("/<string:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    try:
        data = request.get_json()
        logger.info(
            "PUT /employees/%s - Received update payload: %s", employee_id, data
        )

        if not data:
            logger.warning("PUT /employees/%s - Missing request body", employee_id)
            return jsonify({"error": ERR_BODY_REQUIRED}), STATUS_BAD_REQUEST

        validated_data = UpdateEmployeeRequestDTO(**data)

        employee = EmployeeService.update_employee(
            employee_id=employee_id,
            name=validated_data.name,
            email=validated_data.email,
            department=validated_data.department,
            date_joined=validated_data.date_joined.isoformat()
            if validated_data.date_joined
            else None,
        )

        logger.info("PUT /employees/%s - Successfully updated employee", employee_id)
        return jsonify(
            UpdateEmployeeResponseDTO(**employee).model_dump(mode="json")
        ), STATUS_OK

    except ValidationError as e:
        safe_errors = [
            {"loc": err.get("loc"), "msg": err.get("msg"), "type": err.get("type")}
            for err in e.errors()
        ]
        logger.warning(
            "PUT /employees/%s - Validation Error: %s", employee_id, safe_errors
        )
        return jsonify(
            {"error": ERR_VALIDATION_FAILED, "details": safe_errors}
        ), STATUS_BAD_REQUEST
    except APIError as e:
        logger.warning("PUT /employees/%s - API Error: %s", employee_id, e.message)
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        logger.exception("PUT /employees/%s - Unexpected error occurred", employee_id)
        return jsonify({"error": ERR_INTERNAL_SERVER}), STATUS_INTERNAL_ERROR


@employee_bp.route("/<string:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    try:
        logger.info("DELETE /employees/%s - Deleting employee", employee_id)
        result = EmployeeService.delete_employee(employee_id)
        logger.info("DELETE /employees/%s - Successfully deleted employee", employee_id)
        return jsonify(
            DeleteEmployeeResponseDTO(**result).model_dump(mode="json")
        ), STATUS_OK
    except APIError as e:
        logger.warning("DELETE /employees/%s - API Error: %s", employee_id, e.message)
        return jsonify({"error": e.message}), e.status_code
    except Exception as e:
        logger.exception(
            "DELETE /employees/%s - Unexpected error occurred", employee_id
        )
        return jsonify({"error": ERR_INTERNAL_SERVER}), STATUS_INTERNAL_ERROR
