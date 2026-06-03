import logging
import uuid
from repositories.employee_repository import EmployeeRepository
from datetime import datetime
from typing import Dict, Any, List
from utils.constants import (
    APIError,
    STATUS_NOT_FOUND,
    STATUS_CONFLICT,
    STATUS_BAD_REQUEST,
    ERR_INVALID_UUID,
    ERR_EMAIL_EXISTS,
    ERR_EMAIL_IN_USE,
    ERR_EMPLOYEE_NOT_FOUND,
    MSG_DELETE_SUCCESS,
)

logger = logging.getLogger(__name__)


class EmployeeService:
    @staticmethod
    def validate_employee_data(name: str, email: str, department: str) -> None:
        pass

    @staticmethod
    def create_employee(
        name: str, email: str, department: str, date_joined: str
    ) -> Dict[str, Any]:
        logger.info("Service - Attempting to create employee with email: %s", email)
        # Validation
        EmployeeService.validate_employee_data(name, email, department)

        # Check if email already exists
        if EmployeeRepository.get_employee_by_email(email):
            logger.warning(
                "Service - Email conflict: Employee with email %s already exists", email
            )
            raise APIError(ERR_EMAIL_EXISTS.format(email=email), STATUS_CONFLICT)

        joined_date = datetime.strptime(date_joined, "%Y-%m-%d").date()

        # Create employee
        employee = EmployeeRepository.create_employee(
            name, email, department, joined_date
        )
        logger.info(
            "Service - Employee successfully created in DB with ID: %s", employee.id
        )
        return employee.to_dict()

    @staticmethod
    def get_employee(employee_id: str) -> Dict[str, Any]:
        logger.info("Service - Fetching employee with ID: %s", employee_id)
        if not isinstance(employee_id, str):
            logger.warning("Service - Invalid ID type: %s", type(employee_id))
            raise APIError(ERR_INVALID_UUID, STATUS_BAD_REQUEST)
        try:
            uuid.UUID(employee_id)
        except ValueError:
            logger.warning("Service - Invalid UUID string format: %s", employee_id)
            raise APIError(ERR_INVALID_UUID, STATUS_BAD_REQUEST)

        employee = EmployeeRepository.get_employee_by_id(employee_id)
        if not employee:
            logger.warning("Service - Employee with ID %s not found in DB", employee_id)
            raise APIError(
                ERR_EMPLOYEE_NOT_FOUND.format(employee_id=employee_id), STATUS_NOT_FOUND
            )

        logger.info("Service - Employee with ID %s successfully retrieved", employee_id)
        return employee.to_dict()

    @staticmethod
    def get_all_employees() -> List[Dict[str, Any]]:
        logger.info("Service - Fetching all employees list")
        employees = EmployeeRepository.get_all_employees()
        return [employee.to_dict() for employee in employees]

    @staticmethod
    def update_employee(
        employee_id: str,
        name: str = None,
        email: str = None,
        department: str = None,
        date_joined: str = None,
    ) -> Dict[str, Any]:
        logger.info("Service - Attempting to update employee ID: %s", employee_id)
        if not isinstance(employee_id, str):
            logger.warning("Service - Invalid ID type: %s", type(employee_id))
            raise APIError(ERR_INVALID_UUID, STATUS_BAD_REQUEST)
        try:
            uuid.UUID(employee_id)
        except ValueError:
            logger.warning("Service - Invalid UUID string format: %s", employee_id)
            raise APIError(ERR_INVALID_UUID, STATUS_BAD_REQUEST)

        # Check if employee exists
        employee = EmployeeRepository.get_employee_by_id(employee_id)
        if not employee:
            logger.warning(
                "Service - Employee with ID %s not found for update", employee_id
            )
            raise APIError(
                ERR_EMPLOYEE_NOT_FOUND.format(employee_id=employee_id), STATUS_NOT_FOUND
            )

        # Prepare update data
        update_data = {}

        if name is not None:
            update_data["name"] = name

        if email is not None:
            # Check if email is already used by another employee
            if EmployeeRepository.employee_exists_by_email(
                email, exclude_id=employee_id
            ):
                logger.warning(
                    "Service - Email conflict: Email %s already in use by another record",
                    email,
                )
                raise APIError(ERR_EMAIL_IN_USE.format(email=email), STATUS_CONFLICT)
            update_data["email"] = email

        if department is not None:
            update_data["department"] = department

        if date_joined is not None:
            joined_date = datetime.strptime(date_joined, "%Y-%m-%d").date()
            update_data["date_joined"] = joined_date

        # Update employee
        updated_employee = EmployeeRepository.update_employee(
            employee_id, **update_data
        )
        logger.info("Service - Employee ID %s updated successfully", employee_id)
        return updated_employee.to_dict()

    @staticmethod
    def delete_employee(employee_id: str) -> Dict[str, str]:
        logger.info("Service - Attempting to delete employee ID: %s", employee_id)
        if not isinstance(employee_id, str):
            logger.warning("Service - Invalid ID type: %s", type(employee_id))
            raise APIError(ERR_INVALID_UUID, STATUS_BAD_REQUEST)
        try:
            uuid.UUID(employee_id)
        except ValueError:
            logger.warning("Service - Invalid UUID string format: %s", employee_id)
            raise APIError(ERR_INVALID_UUID, STATUS_BAD_REQUEST)

        # Check if employee exists
        if not EmployeeRepository.get_employee_by_id(employee_id):
            logger.warning(
                "Service - Employee with ID %s not found for deletion", employee_id
            )
            raise APIError(
                ERR_EMPLOYEE_NOT_FOUND.format(employee_id=employee_id), STATUS_NOT_FOUND
            )

        # Delete employee
        EmployeeRepository.delete_employee(employee_id)
        logger.info(
            "Service - Employee ID %s deleted successfully from DB", employee_id
        )
        return {"message": MSG_DELETE_SUCCESS.format(employee_id=employee_id)}
