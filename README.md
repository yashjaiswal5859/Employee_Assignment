# Employee Management System

A simple Employee Management System built with Python, Flask, and SQLAlchemy using a layered architecture (Controller → Service → Repository). Uses PostgreSQL as the database.

## Project Structure

```
Backend/
├── app.py                          # Application entry point
├── config.py                       # Configuration (reads from .env)
├── models.py                       # SQLAlchemy Employee model
├── controllers/
│   └── employee_controller.py      # API routes (Controller Layer)
├── services/
│   └── employee_service.py         # Business logic (Service Layer)
├── repositories/
│   └── employee_repository.py      # Database access (Repository Layer)
├── tests/                          # Unit tests for each layer
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup PostgreSQL Database

Make sure PostgreSQL is installed and running. Then create the database:

```sql
CREATE DATABASE employee_db;
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file with your PostgreSQL credentials:

```
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/employee_db
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/employee_test_db
```

### 5. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Create Employee
**POST** `/employees`

Request:
```json
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "department": "Engineering",
    "date_joined": "2024-01-15"
}
```

Response `201 Created`:
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "department": "Engineering",
    "date_joined": "2024-01-15"
}
```

### 2. Get All Employees
**GET** `/employees`

Response `200 OK`:
```json
[
    {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "department": "Engineering",
        "date_joined": "2024-01-15"
    }
]
```

### 3. Get Employee by ID
**GET** `/employees/{id}`

Response `200 OK`:
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "department": "Engineering",
    "date_joined": "2024-01-15"
}
```

### 4. Update Employee
**PUT** `/employees/{id}`

Request (all fields optional):
```json
{
    "name": "Jane Doe",
    "department": "Marketing"
}
```

Response `200 OK`:
```json
{
    "id": 1,
    "name": "Jane Doe",
    "email": "john.doe@example.com",
    "department": "Marketing",
    "date_joined": "2024-01-15"
}
```

### 5. Delete Employee
**DELETE** `/employees/{id}`

Response `200 OK`:
```json
{
    "message": "Employee with ID 1 deleted successfully"
}
```

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input or validation error |
| 404 | Not Found - Employee not found |
| 500 | Internal Server Error |

Error format:
```json
{
    "error": "Error message"
}
```

## Data Validation (Service Layer)

- **name**: Minimum 2 characters
- **email**: Must contain `@` and a `.` in the domain
- **department**: Minimum 2 characters
- **date_joined**: Format `YYYY-MM-DD`, cannot be in the future
- **email**: Must be unique across all employees

## Architecture

```
Client Request
    ↓
Controller Layer (employee_controller.py)
    → Receives HTTP requests, sends HTTP responses
    ↓
Service Layer (employee_service.py)
    → Business logic, validation, orchestration
    ↓
Repository Layer (employee_repository.py)
    → Database CRUD operations via SQLAlchemy ORM
    ↓
PostgreSQL Database
```

## Running Tests

Create a test database first:
```sql
CREATE DATABASE employee_test_db;
```

Then run:
```bash
pytest
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/employee_db` |
| `TEST_DATABASE_URL` | Test database connection string | `postgresql://postgres:postgres@localhost:5432/employee_test_db` |
| `FLASK_ENV` | Flask environment | `development` |
