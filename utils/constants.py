# HTTP Status Codes
STATUS_OK = 200
STATUS_CREATED = 201
STATUS_BAD_REQUEST = 400
STATUS_NOT_FOUND = 404
STATUS_CONFLICT = 409
STATUS_INTERNAL_ERROR = 500

# Error Messages
ERR_INVALID_UUID = "Invalid employee ID format"
ERR_BODY_REQUIRED = "Request body is required"
ERR_VALIDATION_FAILED = "Validation Error"
ERR_INTERNAL_SERVER = "Internal server error"
ERR_EMAIL_EXISTS = "Employee with email {email} already exists"
ERR_EMAIL_IN_USE = "Email {email} is already in use"
ERR_EMPLOYEE_NOT_FOUND = "Employee with ID {employee_id} not found"

# Success Messages
MSG_DELETE_SUCCESS = "Employee with ID {employee_id} deleted successfully"
MSG_API_HOME = "Employee Management System API"


class APIError(Exception):
    """Custom exception carrying a descriptive error message and its matching HTTP status code."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
