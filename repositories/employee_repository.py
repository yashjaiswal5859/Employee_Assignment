import logging
from typing import List, Optional
from models.employee_model import Employee
from core.db import get_master_session, get_replica_session

logger = logging.getLogger(__name__)


class EmployeeRepository:
    @staticmethod
    def create_employee(
        name: str, email: str, department: str, date_joined
    ) -> Employee:
        logger.debug("DB Write - Creating employee record in Master DB: %s", email)
        session = get_master_session()
        try:
            employee = Employee(
                name=name, email=email, department=department, date_joined=date_joined
            )
            session.add(employee)
            session.commit()
            session.refresh(employee)
            return employee
        finally:
            session.close()

    @staticmethod
    def get_employee_by_id(employee_id: str) -> Optional[Employee]:
        logger.debug(
            "DB Read - Fetching employee by ID from Replica DB: %s", employee_id
        )
        session = get_replica_session()
        try:
            return session.get(Employee, employee_id)
        finally:
            session.close()

    @staticmethod
    def get_employee_by_email(email: str) -> Optional[Employee]:
        logger.debug("DB Read - Fetching employee by email from Replica DB: %s", email)
        session = get_replica_session()
        try:
            return session.query(Employee).filter_by(email=email).first()
        finally:
            session.close()

    @staticmethod
    def get_all_employees() -> List[Employee]:
        logger.debug("DB Read - Fetching all employee records from Replica DB")
        session = get_replica_session()
        try:
            return session.query(Employee).all()
        finally:
            session.close()

    @staticmethod
    def update_employee(employee_id: str, **kwargs) -> Optional[Employee]:
        logger.debug(
            "DB Write - Updating employee record in Master DB: %s", employee_id
        )
        session = get_master_session()
        try:
            employee = session.get(Employee, employee_id)
            if not employee:
                return None

            for key, value in kwargs.items():
                if hasattr(employee, key) and key not in ["id", "created_at"]:
                    setattr(employee, key, value)

            session.commit()
            session.refresh(employee)
            return employee
        finally:
            session.close()

    @staticmethod
    def delete_employee(employee_id: str) -> bool:
        logger.debug(
            "DB Write - Deleting employee record in Master DB: %s", employee_id
        )
        session = get_master_session()
        try:
            employee = session.get(Employee, employee_id)
            if not employee:
                return False

            session.delete(employee)
            session.commit()
            return True
        finally:
            session.close()

    @staticmethod
    def employee_exists_by_email(email: str, exclude_id: str = None) -> bool:
        logger.debug(
            "DB Read - Checking email existence in Master DB: %s (exclude: %s)",
            email,
            exclude_id,
        )
        session = get_master_session()
        try:
            query = session.query(Employee).filter_by(email=email)
            if exclude_id:
                query = query.filter(Employee.id != exclude_id)
            return query.first() is not None
        finally:
            session.close()
