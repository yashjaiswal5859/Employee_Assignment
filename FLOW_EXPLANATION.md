# Employee Management System — Complete Flow Explanation

This document explains **everything** that happens in this project — from the moment you start the databases to the moment an API request is processed. Every step is explained in simple language with examples.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Step 1 — Start Databases (docker compose up)](#2-step-1--start-databases-docker-compose-up)
3. [Step 2 — Start Flask App (python app.py)](#3-step-2--start-flask-app-python-apppy)
4. [Step 3 — API Request Flow (with examples)](#4-step-3--api-request-flow-with-examples)
5. [Step 4 — WAL Replication (how data syncs)](#5-step-4--wal-replication-how-data-syncs)
6. [Step 5 — Testing (python app.py --test)](#6-step-5--testing-python-apppy---test)
7. [File-by-File Explanation](#7-file-by-file-explanation)

---

## 1. Project Structure

```
Backend/
├── app.py                            # Application entry point (runs server or tests)
├── core/
│   ├── config.py                     # Configuration loader (reads from .env)
│   ├── db.py                         # Master & Replica session connection setup
│   └── logger.py                     # Structured logging configuration
├── utils/
│   └── constants.py                  # APIError exception, HTTP statuses & messaging
├── models/
│   └── employee_model.py             # SQLAlchemy Database Model for Employees
├── dtos/
│   ├── request/
│   │   └── employee_request.py       # Pydantic Request validation DTOs
│   └── response/
│       └── employee_response.py      # Pydantic Response formatting DTOs
├── controllers/
│   └── employee_controller.py        # Controller Layer (HTTP routes & DTO matching)
├── services/
│   └── employee_service.py           # Service Layer (Business logic & domain checks)
├── repositories/
│   └── employee_repository.py        # Repository Layer (Direct database queries)
├── migrations/
│   ├── 1717334640_initial_up.sql      # Main schema setup migration (creates table)
│   ├── 1717334640_initial_down.sql    # Main schema teardown migration (drops table)
│   └── README.md                     # Migration execution documentation
├── docker/
│   └── postgres/
│       ├── create-replication-user.sh # Runs on Master (creates replicator user/slot)
│       └── setup-replica.sh          # Runs on Replica (clones Master and sets standby)
└── tests/
    ├── test_runner.py                # Automated migration-based integration test runner
    └── migrations/
        ├── test_up.sql               # Creates employees table in test database
        ├── test_seed.sql             # Seeds 5 dummy records with static UUIDs for tests
        └── test_down.sql             # Teardown test schema (drops table)
```

---

## 2. Step 1 — Start Databases (`docker compose up`)

**Command:**
```bash
docker compose up -d
```

This starts **4 PostgreSQL database containers**:

| Container                | Role             | Host Port | Database Name     |
|--------------------------|------------------|-----------|-------------------|
| `postgres_master_db`     | Main Master      | 5432      | `mydatabase`      |
| `postgres_replica_db`    | Main Replica     | 5433      | `mydatabase`      |
| `postgres_test_master_db`| Test Master      | 5434      | `employee_test_db`|
| `postgres_test_replica_db`| Test Replica    | 5435      | `employee_test_db`|

### What happens inside each container?

---

### 2.1 Master Container Starts First

**File involved:** `docker/postgres/create-replication-user.sh`

When the master container starts for the first time, PostgreSQL automatically runs all scripts inside `/docker-entrypoint-initdb.d/`. Our script does 3 things:

**Step A — Create a replication user:**
```sql
CREATE ROLE replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'secret123';
```
> **Why?** Normal database users cannot access WAL logs. The `replicator` user has special `REPLICATION` permission that allows the replica to connect and stream data.

**Step B — Create a replication slot:**
```sql
SELECT pg_create_physical_replication_slot('replica_slot');
```
> **Why?** A replication slot is like a "bookmark". It tells the master: *"Don't delete any WAL logs until the replica has received them."* Without this, if the replica goes offline temporarily, the master might delete WAL logs that the replica hasn't received yet, breaking replication.

**Step C — Allow replication connections:**
```bash
# Add this line to pg_hba.conf (PostgreSQL's access control file)
host replication replicator 0.0.0.0/0 trust
```
> **Why?** By default, PostgreSQL blocks all replication connections. This line says: *"Allow the user `replicator` to connect for replication from any IP address."*

After these 3 steps, the master is ready and reports `healthy`.

---

### 2.2 Replica Container Starts After Master Is Healthy

**File involved:** `docker/postgres/setup-replica.sh`

The replica container waits until the master reports `healthy`, then runs:

**Step A — Wait for master:**
```bash
until pg_isready -h postgres_master -p 5432 -U replicator; do
    sleep 2
done
```
> Keeps checking every 2 seconds: *"Is the master accepting connections?"*

**Step B — Copy entire database from master:**
```bash
pg_basebackup -h postgres_master -p 5432 -D $PGDATA -U replicator -v -P --wal-method=stream
```
> **What is `pg_basebackup`?** It creates an exact copy of the master's database. Think of it like cloning the master's hard drive. After this, the replica has the same tables, data, users — everything identical to the master.

**Step C — Configure replica as read-only standby:**
```bash
# Write connection info to postgresql.conf
primary_conninfo = 'host=postgres_master port=5432 user=replicator password=secret123'
primary_slot_name = 'replica_slot'
hot_standby = on

# Create the standby signal file
touch $PGDATA/standby.signal
```

> **`standby.signal`** — This file tells PostgreSQL: *"You are a replica. Do NOT accept any writes. Only receive data from the master."*
>
> **`hot_standby = on`** — This tells PostgreSQL: *"Even though you are a replica, allow clients to connect and run SELECT (read) queries."*
>
> **`primary_conninfo`** — This tells the replica: *"Here is the master's address. Connect to it and start streaming WAL logs."*

**Step D — Start PostgreSQL:**
```bash
exec docker-entrypoint.sh postgres
```
> Starts the replica server. It immediately connects to the master and begins streaming WAL logs in real-time.

---

### 2.3 After Both Are Running

```
Master (port 5432)                     Replica (port 5433)
┌──────────────────┐                  ┌──────────────────┐
│  Can READ        │   WAL Stream     │  Can READ        │
│  Can WRITE       │ ──────────────>  │  CANNOT WRITE    │
│                  │  (real-time)     │                  │
│  employees table │                  │  employees table │
│  (same data)     │                  │  (same data)     │
└──────────────────┘                  └──────────────────┘
```

The same setup happens for the **test databases** (ports 5434 and 5435).

---

## 3. Step 2 — Start Flask App (`python app.py`)

**Command:**
```bash
python app.py
```

Here is what happens step by step:

### 3.1 Parse Command Line Arguments

```python
# app.py (line 59-66)
parser = argparse.ArgumentParser()
parser.add_argument('--test', action='store_true')
args = parser.parse_args()
```

- If you ran `python app.py` → starts the web server
- If you ran `python app.py --test` → runs the test suite (explained in Section 6)

### 3.2 Load Configuration

```python
# core/config.py
load_dotenv()  # Reads .env file

MASTER_DATABASE_URL = os.getenv('MASTER_DATABASE_URL')
# Result: "postgresql://employee:secret123@localhost:5432/mydatabase"

REPLICA_DATABASE_URL = os.getenv('REPLICA_DATABASE_URL')
# Result: "postgresql://employee:secret123@localhost:5433/mydatabase"
```

> The `.env` file contains the database connection URLs. The app reads them at startup.

### 3.3 Create Database Connections

```python
# core/db.py
master_engine = create_engine("postgresql://...@localhost:5432/mydatabase")
replica_engine = create_engine("postgresql://...@localhost:5433/mydatabase")

MasterSession = sessionmaker(bind=master_engine)   # For writes
ReplicaSession = sessionmaker(bind=replica_engine)  # For reads
```

> **Engine** = a connection pool to a database. It doesn't open a connection immediately; it creates connections when needed.
>
> **Session** = a temporary conversation with the database. You open a session, run queries, then close it.

### 3.4 Create Tables (Migration)

```python
# app.py (line 19-31)
with app.app_context():
    db.create_all()  # Creates 'employees' table on Master
```

> This checks: *"Does the `employees` table exist on the master?"*
> - If **NO** → creates it
> - If **YES** → does nothing
>
> The replica gets this table automatically via WAL replication (no need to create it separately).

### 3.5 Register Routes and Start Server

```python
app.register_blueprint(employee_bp)  # Registers all /employees routes
app.run(host='0.0.0.0', port=5000)   # Starts listening on port 5000
```

**Output:**
```
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

The server is now ready to accept API requests.

---

## 4. Step 3 — API Request Flow (with examples)

The app has 5 API endpoints. Each request flows through 3 layers:

```
HTTP Request
    │
    ▼
┌─────────────────────────┐
│  Controller              │   Receives request, extracts JSON data
│  (employee_controller)   │   Returns JSON response
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Service                 │   Validates data (name length, email format, etc.)
│  (employee_service)      │   Throws errors if validation fails
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Repository              │   Runs actual SQL queries
│  (employee_repository)   │   WRITES go to Master, READS go to Replica
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Database                │
│  Master (write) ← WAL → Replica (read)
└─────────────────────────┘
```

---

### 4.1 POST /employees — Create Employee (WRITE → Master)

**Request:**
```bash
curl -X POST http://localhost:5000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering",
    "date_joined": "2024-06-01"
  }'
```

**What happens step by step:**

| Step | Layer | What happens |
|------|-------|-------------|
| 1 | **Controller** | Receives JSON body. Strictly validates types, lengths, and formats using **Pydantic Request DTOs**. |
| 2 | **Service** | Executes business logic: Checks if email already exists (queries **Replica**). |
| 3 | **Repository** | Opens a session on **Master** (`get_master_session()`). |
| 4 | **Repository** | Runs `INSERT INTO employees (id, name, email, department, date_joined) VALUES (...)` using a generated UUID. |
| 5 | **Repository** | Commits the transaction. |
| 6 | **WAL Replication** | Master sends this INSERT to Replica via WAL stream. Replica now has the same row. |
| 7 | **Controller** | Formats the inserted data through a strict **Pydantic Response DTO** before returning to the client. |

**Response (201 Created):**
```json
{
  "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "date_joined": "2024-06-01"
}
```

**Validation Error Example — Short name:**
```bash
curl -X POST http://localhost:5000/employees \
  -d '{"name": "J", "email": "j@test.com", "department": "HR", "date_joined": "2024-01-01"}'
```
**Response (400 Bad Request):**
```json
{"error": "Name must be at least 2 characters long"}
```

---

### 4.2 GET /employees — Get All Employees (READ → Replica)

**Request:**
```bash
curl http://localhost:5000/employees
```

**What happens:**

| Step | Layer | What happens |
|------|-------|-------------|
| 1 | **Controller** | Receives the GET request. |
| 2 | **Service** | Calls repository to fetch all employees. |
| 3 | **Repository** | Opens a session on **Replica** (`get_replica_session()`). |
| 4 | **Repository** | Runs `SELECT * FROM employees`. |

**Response (200 OK):**
```json
[
  {
    "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering",
    "date_joined": "2024-06-01"
  }
]
```

> **Key Point:** This query runs on the **Replica** database, NOT the Master. This distributes the read load away from the Master.

---

### 4.3 GET /employees/{uuid} — Get Employee by ID (READ → Replica)

**Request:**
```bash
curl http://localhost:5000/employees/11111111-1111-1111-1111-111111111111
```

**What happens step by step:**

| Step | Layer | What happens |
|------|-------|-------------|
| 1 | **Controller** | Extracts `employee_id = "11111111-1111-1111-1111-111111111111"` from the URL. |
| 2 | **Service** | Validates that the ID is a valid UUID string format. |
| 3 | **Repository** | Opens a session on **Replica**. |
| 4 | **Repository** | Runs `SELECT * FROM employees WHERE id = '11111111-1111-1111-1111-111111111111'`. |

**Response (200 OK):**
```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering",
  "date_joined": "2024-06-01"
}
```

**Not Found Example:**
```bash
curl http://localhost:5000/employees/99999999-9999-9999-9999-999999999999
```
**Response (404 Not Found):**
```json
{"error": "Employee with ID 99999999-9999-9999-9999-999999999999 not found"}
```

---

### 4.4 PUT /employees/{uuid} — Update Employee (WRITE → Master)

**Request:**
```bash
curl -X PUT http://localhost:5000/employees/11111111-1111-1111-1111-111111111111 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated",
    "department": "Management"
  }'
```

**What happens:**

| Step | Layer | What happens |
|------|-------|-------------|
| 1 | **Controller** | Extracts `employee_id = "11111111-1111-1111-1111-111111111111"` and strictly validates the JSON body using a **Pydantic Request DTO**. |
| 2 | **Service** | Checks if employee with that ID exists (queries **Replica**). |
| 3 | **Service** | Checks for duplicate email if email is being changed (queries **Replica**). |
| 4 | **Repository** | Opens a session on **Master** (`get_master_session()`). |
| 5 | **Repository** | Runs `UPDATE employees SET name='John Updated', department='Management' WHERE id='11111111-1111-1111-1111-111111111111'`. |
| 6 | **Repository** | Commits the transaction. |
| 7 | **WAL Replication** | Master sends this UPDATE to Replica. |
| 8 | **Controller** | Formats the updated data through a strict **Pydantic Response DTO**. |

**Response (200 OK):**
```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "name": "John Updated",
  "email": "john@example.com",
  "department": "Management",
  "date_joined": "2024-06-01"
}
```

---

### 4.5 DELETE /employees/{uuid} — Delete Employee (WRITE → Master)

**Request:**
```bash
curl -X DELETE http://localhost:5000/employees/11111111-1111-1111-1111-111111111111
```

**What happens:**

| Step | Layer | What happens |
|------|-------|-------------|
| 1 | **Controller** | Extracts `employee_id = "11111111-1111-1111-1111-111111111111"`. |
| 2 | **Service** | Checks if employee exists (queries **Replica**). |
| 3 | **Repository** | Opens a session on **Master** (`get_master_session()`). |
| 4 | **Repository** | Runs `DELETE FROM employees WHERE id = '11111111-1111-1111-1111-111111111111'`. |
| 5 | **Repository** | Commits the transaction. |
| 6 | **WAL Replication** | Master sends this DELETE to Replica. Row is removed from Replica too. |

**Response (200 OK):**
```json
{"message": "Employee with ID 11111111-1111-1111-1111-111111111111 deleted successfully"}
```

---

## 5. Step 4 — WAL Replication (how data syncs)

**WAL** stands for **Write-Ahead Log**. It is PostgreSQL's internal diary.

### How it works (simple explanation):

```
1. You INSERT a row on the Master.

2. Before actually writing to the table, the Master writes
   a log entry: "INSERT row with id='9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d', name=John, email=john@example.com..."
   This log entry is called a WAL record.

3. The Master sends this WAL record to the Replica over the network
   (via the streaming connection established during setup).

4. The Replica receives the WAL record and applies it to its own database.
   Now the Replica also has the row with id='9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'.

5. This happens in real-time (milliseconds).
```

### Visual diagram:

```
  Your App                Master DB                    Replica DB
    │                        │                              │
    │  INSERT employee       │                              │
    │ ─────────────────────> │                              │
    │                        │                              │
    │                        │  1. Write WAL record         │
    │                        │  2. Insert into table        │
    │                        │                              │
    │  Response: {id: uuid}  │                              │
    │ <───────────────────── │                              │
    │                        │                              │
    │                        │  3. Stream WAL to Replica    │
    │                        │ ──────────────────────────>  │
    │                        │                              │
    │                        │                              │  4. Apply WAL record
    │                        │                              │     (row appears here too)
    │                        │                              │
    │  GET all employees     │                              │
    │ ─────────────────────────────────────────────────────>│
    │                        │                              │
    │  Response: [{id: uuid}]│                              │
    │ <─────────────────────────────────────────────────────│
```

### What gets replicated?

| Operation | Replicated? |
|-----------|-------------|
| `INSERT INTO employees ...` | ✅ Yes |
| `UPDATE employees SET ...` | ✅ Yes |
| `DELETE FROM employees ...` | ✅ Yes |
| `CREATE TABLE employees ...` | ✅ Yes |
| `DROP TABLE employees` | ✅ Yes |

**Everything** that modifies data on the Master is automatically replicated to the Replica.

---

## 6. Step 5 — Testing (`python app.py --test`)

**Command:**
```bash
python app.py --test
```

When you pass the `--test` flag, the app does NOT start the web server. Instead, it runs the test suite.

### Test Flow (4 phases):

```
PHASE 1: UP Migration
    Run test_up.sql on Test Master
    → Creates employees table
    → WAL replication creates it on Test Replica automatically

PHASE 2: Seed Data
    Run test_seed.sql on Test Master
    → Inserts 5 dummy employees
    → WAL replication copies them to Test Replica automatically

PHASE 3: Run 18 Test Cases
    Each test:
      1. Prepares mock data
      2. Uses the Flask `test_client()` to make a real HTTP request to the API route
      3. The API runs through the Controller, DTO validation, Service, and DB
      4. Compares actual HTTP Response code and JSON vs expected result
      5. Prints [PASS] or [FAIL]

PHASE 4: DOWN Migration (Cleanup)
    Run test_down.sql on Test Master
    → Drops employees table
    → WAL replication drops it on Test Replica automatically
```

### The 18 Test Cases:

| # | Test | What it checks |
|---|------|----------------|
| 1 | CREATE valid employee | Insert works, returns id + name + email |
| 2 | CREATE short name | Rejects name with less than 2 characters |
| 3 | CREATE invalid email | Rejects email without `@` or `.` |
| 4 | CREATE short department | Rejects department with less than 2 characters |
| 5 | CREATE duplicate email | Rejects email that already exists in DB |
| 6 | CREATE future date | Rejects date_joined that is in the future |
| 7 | CREATE bad date format | Rejects date like "01-15-2024" (must be YYYY-MM-DD) |
| 8 | GET ALL employees | Returns list of 6 employees (5 seeded + 1 created in test #1) |
| 9 | GET BY ID (valid) | Returns correct employee for seeded UUID |
| 10 | GET BY ID (invalid format) | Rejects bad UUID format like "1" with 400 Bad Request |
| 11 | GET BY ID (not found) | Throws error for non-existent UUID |
| 12 | UPDATE valid | Updates name and department successfully |
| 13 | UPDATE not found | Throws error for non-existent UUID |
| 14 | UPDATE short name | Rejects updated name with less than 2 characters |
| 15 | UPDATE duplicate email | Rejects email that belongs to another employee |
| 16 | DELETE valid | Deletes employee with seeded UUID successfully |
| 17 | DELETE not found | Throws error for non-existent UUID |
| 18 | DELETE verify gone | Confirms deleted employee no longer exists in DB |

### Example Output:
```
============================================================
  MIGRATION TEST RUNNER
============================================================

  Reading migration files...

-- PHASE 1 - UP Migration (tests/migrations/test_up.sql) --
  [OK] UP migration on TEST MASTER
  [OK] Schema replicated to TEST REPLICA automatically

-- PHASE 2 - Seed Data (tests/migrations/test_seed.sql) --
  [OK] Seed data on TEST MASTER
  [OK] Seed data replicated to TEST REPLICA automatically

-- PHASE 3 - Tests: CREATE Employee (HTTP -> Pydantic -> DB) --
  CREATE - valid employee                                 [PASS]
  CREATE - reject short name (len < 2) [Pydantic]         [PASS]
  CREATE - reject invalid email [Pydantic]                [PASS]
  ...

-- PHASE 3 - Tests: GET Employee(s) --
  GET ALL - returns list (expected 6, got 6)              [PASS]
  GET BY ID - valid id (id=11111111-1111-1111-1111-111111111111) [PASS]
  GET BY ID - reject invalid UUID format                  [PASS]
  GET BY ID - not found (id=99999999-9999-9999-9999-999999999999) [PASS]

-- PHASE 3 - Tests: UPDATE Employee (HTTP -> Pydantic -> DB) --
  UPDATE - valid update (id=11111111-1111-1111-1111-111111111111, name+dept) [PASS]
  UPDATE - not found (id=99999999-9999-9999-9999-999999999999) [PASS]
  UPDATE - reject short name (len < 2) [Pydantic]         [PASS]
  UPDATE - reject duplicate email                         [PASS]

-- PHASE 3 - Tests: DELETE Employee --
  DELETE - valid delete (id=11111111-1111-1111-1111-111111111111) [PASS]
  DELETE - not found (id=99999999-9999-9999-9999-999999999999) [PASS]

-- PHASE 3 - Tests: Verify DELETE --
  GET BY ID - not found (id=11111111-1111-1111-1111-111111111111) [PASS]

-- PHASE 4 - DOWN Migration (tests/migrations/test_down.sql) --
  [OK] DOWN migration on TEST MASTER

============================================================
  TEST RESULTS SUMMARY
============================================================

  Total : 18
  Passed: 18
  Failed: 0

  >>> ALL TESTS PASSED <<<
```

---

## 7. File-by-File Explanation

### 7.1 `.env` — Environment Variables

```env
MASTER_DATABASE_URL=postgresql://employee:secret123@localhost:5432/mydatabase
REPLICA_DATABASE_URL=postgresql://employee:secret123@localhost:5433/mydatabase
TEST_MASTER_DATABASE_URL=postgresql://employee:secret123@localhost:5434/employee_test_db
TEST_REPLICA_DATABASE_URL=postgresql://employee:secret123@localhost:5435/employee_test_db
```

> Format: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE_NAME`
>
> The app reads these URLs to know where the Master and Replica databases are running.

---

### 7.2 `core/config.py` — Configuration Loader

**What it does:** Reads the `.env` file and makes the database URLs available to the rest of the app.

```python
load_dotenv()  # Load .env file
MASTER_DATABASE_URL = os.getenv('MASTER_DATABASE_URL')
REPLICA_DATABASE_URL = os.getenv('REPLICA_DATABASE_URL')
```

---

### 7.3 `core/db.py` — Database Connection Manager

**What it does:** Creates two database connection pools (engines) and two session factories.

- `master_engine` + `MasterSession` → connects to **Master** (port 5432) → used for **writes**
- `replica_engine` + `ReplicaSession` → connects to **Replica** (port 5433) → used for **reads**

**Key functions:**
- `get_master_session()` → returns a new session connected to Master
- `get_replica_session()` → returns a new session connected to Replica

---

### 7.4 `models/employee_model.py` — Database Table Definition

**What it does:** Defines the `employees` table structure using SQLAlchemy.

```python
class Employee(db.Model):
    __tablename__ = 'employees'

    id          = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # UUID Primary Key
    name        = db.Column(db.String(120), nullable=False)      # Required
    email       = db.Column(db.String(120), unique=True)         # Required + Unique
    department  = db.Column(db.String(100), nullable=False)      # Required
    date_joined = db.Column(db.Date, nullable=False)             # Required
```

> When `db.create_all()` runs, SQLAlchemy reads this class and creates the actual SQL table if it doesn't exist.

---

### 7.5 `controllers/employee_controller.py` — HTTP Request Handler

**What it does:** Receives HTTP requests, extracts data, calls the Service layer, and returns JSON responses.

| Route | Method | What it does |
|-------|--------|-------------|
| `/employees` | POST | Create new employee |
| `/employees` | GET | Get all employees |
| `/employees/<uuid>` | GET | Get one employee by UUID |
| `/employees/<uuid>` | PUT | Update employee |
| `/employees/<uuid>` | DELETE | Delete employee |

> **Strict Boundaries:** The Controller uses Pydantic **Request DTOs** (e.g. `CreateEmployeeRequestDTO`) to strictly validate incoming JSON. It uses **Response DTOs** to cleanly format outgoing data. It does NOT contain business logic or DB queries.

---

### 7.6 `services/employee_service.py` — Business Logic

**What it does:** Contains business rules that cannot be validated simply by checking data types.

**Rules enforced:**
- Email must be unique (no duplicates in the database)
- Employee ID must exist before updating or deleting

> Note: Basic data validation (length, email formats, dates) happens in the Controller layer via Pydantic DTOs before data ever reaches the Service.

---

### 7.7 `repositories/employee_repository.py` — Database Queries

**What it does:** Executes raw database operations. This is the **only** layer that talks to the database directly.

**The key rule:**
- **Writes** (create, update, delete) → use `get_master_session()` → goes to **Master**
- **Reads** (get by id, get all, get by email) → use `get_replica_session()` → goes to **Replica**

---

### 7.8 `docker-compose.yml` — Container Definitions

**What it does:** Defines the 4 database containers and their configuration.

| Service | Port | Role | Shell Script |
|---------|------|------|-------------|
| `postgres_master` | 5432 | Main Master (read + write) | `create-replication-user.sh` |
| `postgres_replica` | 5433 | Main Replica (read only) | `setup-replica.sh` |
| `postgres_test_master` | 5434 | Test Master (read + write) | `create-replication-user.sh` |
| `postgres_test_replica` | 5435 | Test Replica (read only) | `setup-replica.sh` |

---

### 7.9 `docker/postgres/create-replication-user.sh` — Master Setup Script

**Runs on:** Master containers only (at first startup)

**What it does (3 things):**
1. Creates the `replicator` database user with `REPLICATION` permission
2. Creates a physical replication slot (bookmark for WAL logs)
3. Adds a line to `pg_hba.conf` allowing replication connections

---

### 7.10 `docker/postgres/setup-replica.sh` — Replica Setup Script

**Runs on:** Replica containers only (at first startup)

**What it does (4 things):**
1. Waits for the master to be ready
2. Copies the entire master database using `pg_basebackup`
3. Configures the replica as a read-only standby (`standby.signal` + `hot_standby = on`)
4. Starts the PostgreSQL server, which begins streaming WAL logs from the master

---

### 7.11 `tests/test_runner.py` — Integration Test Suite

**Runs when:** `python app.py --test`

**What it does:**
1. Reads SQL migration files from `tests/migrations/`
2. Creates the `employees` table on the Test Master (replicates to Test Replica)
3. Seeds 5 dummy employees on the Test Master (replicates to Test Replica)
4. Runs 18 test cases by calling the Flask HTTP test client
5. Compares actual HTTP results vs expected results
6. Drops the `employees` table (cleanup)
7. Prints a summary of passed/failed tests

---

### 7.12 `utils/constants.py` — Constants & Exceptions

**What it does:** Centralizes standard application metadata to avoid hardcoded string values and brittle error string comparisons across application layers.

**Key features:**
1. **HTTP Status Codes**: Centralizes standard response statuses (e.g. `STATUS_BAD_REQUEST = 400`, `STATUS_NOT_FOUND = 404`).
2. **Standard Messaging**: Stores template strings for success and failure JSON payloads.
3. **`APIError` Exception**: A lightweight, custom Python exception class encapsulating an error message along with an HTTP status code. The Service layer raises this directly, and the Controller catches it to respond instantly without needing string matching.

