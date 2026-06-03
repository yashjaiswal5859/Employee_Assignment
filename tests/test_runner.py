"""
Test Runner Module
==================
Runs migration-based integration tests for all API operations via the Flask test client.

Flow:
  1. UP migration   -> Execute test_up.sql on test master & test replica
  2. Seed            -> Execute test_seed.sql on test master
  3. TEST            -> Call API endpoints via test_client with various conditions (PASS/FAIL)
  4. DOWN migration  -> Execute test_down.sql on test master & test replica (cleanup)
"""

import os
import sys
import io
import time
from flask import Flask
from sqlalchemy import create_engine, text


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)


# --- Colour helpers (ANSI) ---

BOLD    = "\033[1m"
GREEN   = "\033[92m"
RED     = "\033[91m"
CYAN    = "\033[96m"
YELLOW  = "\033[93m"
MAGENTA = "\033[95m"
DIM     = "\033[2m"
RESET   = "\033[0m"


# --- Paths to migration SQL files ---

TESTS_DIR      = os.path.dirname(os.path.abspath(__file__))
MIGRATIONS_DIR = os.path.join(TESTS_DIR, "migrations")
UP_SQL_FILE    = os.path.join(MIGRATIONS_DIR, "test_up.sql")
DOWN_SQL_FILE  = os.path.join(MIGRATIONS_DIR, "test_down.sql")
SEED_SQL_FILE  = os.path.join(MIGRATIONS_DIR, "test_seed.sql")


# --- Helpers ---

def _banner(msg, colour=CYAN):
    width = 60
    print(f"\n{colour}{BOLD}{'=' * width}")
    print(f"  {msg}")
    print(f"{'=' * width}{RESET}\n")


def _section(msg, colour=MAGENTA):
    print(f"\n{colour}{BOLD}-- {msg} --{RESET}")


def _status(label, passed):
    icon = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"  {label:<55s} {icon}")
    return passed


def _read_sql_file(filepath):
    """Read and return the contents of a SQL file."""
    if not os.path.isfile(filepath):
        print(f"  {RED}[X] SQL file not found: {filepath}{RESET}")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def _get_db_urls():
    """Return (test_master_url, test_replica_url) from env or defaults."""
    from dotenv import load_dotenv
    load_dotenv()

    master_url = os.getenv(
        'TEST_MASTER_DATABASE_URL',
        'postgresql://employee:secret123@localhost:5434/employee_test_db'
    )
    replica_url = os.getenv(
        'TEST_REPLICA_DATABASE_URL',
        'postgresql://employee:secret123@localhost:5435/employee_test_db'
    )
    return master_url, replica_url


def _run_migration(engine, sql, label):
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        print(f"  {GREEN}[OK]{RESET} {label}")
        return True
    except Exception as exc:
        print(f"  {RED}[X]{RESET} {label}: {exc}")
        return False


def _create_test_app(master_url, replica_url):
    from models.employee_model import db
    from core.db import init_db_connections
    from controllers.employee_controller import employee_bp

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = master_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MASTER_DATABASE_URL'] = master_url
    app.config['REPLICA_DATABASE_URL'] = replica_url

    db.init_app(app)
    init_db_connections(app)
    app.register_blueprint(employee_bp)

    return app


# --- Test cases ---

def _test_create_employee_success(client):
    mock_data = {
        "name": "Test User",
        "email": "test.user@example.com",
        "department": "Engineering",
        "date_joined": "2024-06-01"
    }
    response = client.post('/employees', json=mock_data)
    time.sleep(1)
    actual = response.get_json()
    passed = (
        response.status_code == 201
        and actual.get('name') == "Test User"
        and actual.get('email') == "test.user@example.com"
        and 'id' in actual
    )
    return _status("CREATE - valid employee", passed)


def _test_create_employee_invalid_name(client):
    mock_data = {
        "name": "A",
        "email": "short.name@example.com",
        "department": "HR",
        "date_joined": "2024-06-01"
    }
    response = client.post('/employees', json=mock_data)
    passed = response.status_code == 400 and "Validation Error" in response.get_json().get("error", "")
    return _status("CREATE - reject short name (len < 2) [Pydantic]", passed)


def _test_create_employee_invalid_email(client):
    mock_data = {
        "name": "Bad Email",
        "email": "not-an-email",
        "department": "HR",
        "date_joined": "2024-06-01"
    }
    response = client.post('/employees', json=mock_data)
    passed = response.status_code == 400 and "Validation Error" in response.get_json().get("error", "")
    return _status("CREATE - reject invalid email [Pydantic]", passed)


def _test_create_employee_invalid_department(client):
    mock_data = {
        "name": "Bad Dept",
        "email": "bad.dept@example.com",
        "department": "X",
        "date_joined": "2024-06-01"
    }
    response = client.post('/employees', json=mock_data)
    passed = response.status_code == 400 and "Validation Error" in response.get_json().get("error", "")
    return _status("CREATE - reject short department (len < 2) [Pydantic]", passed)


def _test_create_employee_duplicate_email(client):
    mock_data = {
        "name": "Duplicate Alice",
        "email": "alice.johnson@test.com",
        "department": "HR",
        "date_joined": "2024-06-01"
    }
    response = client.post('/employees', json=mock_data)
    passed = response.status_code == 400 and "already exists" in response.get_json().get("error", "")
    return _status("CREATE - reject duplicate email", passed)


def _test_create_employee_future_date(client):
    mock_data = {
        "name": "Future Guy",
        "email": "future.guy@example.com",
        "department": "HR",
        "date_joined": "2099-01-01"
    }
    response = client.post('/employees', json=mock_data)
    passed = response.status_code == 400 and "Validation Error" in response.get_json().get("error", "")
    return _status("CREATE - reject future date_joined [Pydantic]", passed)


def _test_create_employee_bad_date_format(client):
    mock_data = {
        "name": "Bad Date",
        "email": "bad.date@example.com",
        "department": "HR",
        "date_joined": "01-15-2024"
    }
    response = client.post('/employees', json=mock_data)
    passed = response.status_code == 400 and "Validation Error" in response.get_json().get("error", "")
    return _status("CREATE - reject bad date format (MM-DD-YYYY) [Pydantic]", passed)


def _test_get_all_employees(client):
    response = client.get('/employees')
    actual = response.get_json()
    passed = response.status_code == 200 and isinstance(actual, list) and len(actual) == 6
    return _status(f"GET ALL - returns list (expected 6, got {len(actual) if isinstance(actual, list) else 0})", passed)


def _test_get_employee_by_id_success(client):
    alice_uuid = "11111111-1111-1111-1111-111111111111"
    response = client.get(f'/employees/{alice_uuid}')
    actual = response.get_json()
    passed = response.status_code == 200 and actual.get('id') == alice_uuid and actual.get('name') == "Alice Johnson"
    return _status(f"GET BY ID - valid id (id={alice_uuid})", passed)


def _test_get_employee_by_id_not_found(client, mock_id="99999999-9999-9999-9999-999999999999"):
    response = client.get(f'/employees/{mock_id}')
    passed = response.status_code == 404 and f"Employee with ID {mock_id} not found" in response.get_json().get("error", "")
    return _status(f"GET BY ID - not found (id={mock_id})", passed)


def _test_update_employee_success(client):
    alice_uuid = "11111111-1111-1111-1111-111111111111"
    mock_data = {
        "name": "Alice Updated",
        "department": "Management"
    }
    response = client.put(f'/employees/{alice_uuid}', json=mock_data)
    time.sleep(1)
    actual = response.get_json()
    passed = response.status_code == 200 and actual.get('name') == "Alice Updated" and actual.get('department') == "Management"
    return _status(f"UPDATE - valid update (id={alice_uuid}, name+dept)", passed)


def _test_update_employee_not_found(client):
    mock_id = "99999999-9999-9999-9999-999999999999"
    mock_data = {"name": "Ghost"}
    response = client.put(f'/employees/{mock_id}', json=mock_data)
    passed = response.status_code == 404 and f"Employee with ID {mock_id} not found" in response.get_json().get("error", "")
    return _status(f"UPDATE - not found (id={mock_id})", passed)


def _test_update_employee_invalid_name(client):
    alice_uuid = "11111111-1111-1111-1111-111111111111"
    mock_data = {"name": "A"}
    response = client.put(f'/employees/{alice_uuid}', json=mock_data)
    passed = response.status_code == 400 and "Validation Error" in response.get_json().get("error", "")
    return _status("UPDATE - reject short name (len < 2) [Pydantic]", passed)


def _test_update_employee_duplicate_email(client):
    alice_uuid = "11111111-1111-1111-1111-111111111111"
    mock_data = {"email": "bob.smith@test.com"}
    response = client.put(f'/employees/{alice_uuid}', json=mock_data)
    passed = response.status_code == 400 and "is already in use" in response.get_json().get("error", "")
    return _status("UPDATE - reject duplicate email", passed)


def _test_delete_employee_success(client):
    alice_uuid = "11111111-1111-1111-1111-111111111111"
    response = client.delete(f'/employees/{alice_uuid}')
    time.sleep(1)
    passed = response.status_code == 200 and f"Employee with ID {alice_uuid} deleted successfully" in response.get_json().get("message", "")
    return _status(f"DELETE - valid delete (id={alice_uuid})", passed)


def _test_delete_employee_not_found(client):
    mock_id = "99999999-9999-9999-9999-999999999999"
    response = client.delete(f'/employees/{mock_id}')
    passed = response.status_code == 404 and f"Employee with ID {mock_id} not found" in response.get_json().get("error", "")
    return _status(f"DELETE - not found (id={mock_id})", passed)


# --- Main runner ---

def run_tests():
    _banner("MIGRATION TEST RUNNER")

    print(f"  {DIM}Reading migration files...{RESET}")
    up_sql   = _read_sql_file(UP_SQL_FILE)
    down_sql = _read_sql_file(DOWN_SQL_FILE)
    seed_sql = _read_sql_file(SEED_SQL_FILE)

    if not all([up_sql, down_sql, seed_sql]):
        print(f"\n  {RED}{BOLD}Missing migration SQL files -- aborting.{RESET}\n")
        return 1

    master_url, replica_url = _get_db_urls()
    master_engine  = create_engine(master_url)
    replica_engine = create_engine(replica_url)

    _section("PHASE 1 - UP Migration (tests/migrations/test_up.sql)")
    up_master = _run_migration(master_engine, up_sql, "UP migration on TEST MASTER")
    if up_master:
        print(f"  {GREEN}[OK]{RESET} Schema replicated to TEST REPLICA automatically")
        time.sleep(1)  
    else:
        print(f"\n  {RED}{BOLD}Migration failed -- aborting tests.{RESET}")
        return 1

    _section("PHASE 2 - Seed Data (tests/migrations/test_seed.sql)")
    seed_master = _run_migration(master_engine, seed_sql, "Seed data on TEST MASTER")
    if seed_master:
        print(f"  {GREEN}[OK]{RESET} Seed data replicated to TEST REPLICA automatically")
        time.sleep(1)
    else:
        print(f"\n  {RED}{BOLD}Seeding failed -- aborting tests.{RESET}")
        return 1

    # ============================================================
    # PHASE 3: Run HTTP API tests via Flask test_client
    # ============================================================
    app = _create_test_app(master_url, replica_url)
    client = app.test_client()
    all_results = []

    with app.app_context():

        _section("PHASE 3 - Tests: CREATE Employee (HTTP -> Pydantic -> DB)")
        all_results.append(_test_create_employee_success(client))
        all_results.append(_test_create_employee_invalid_name(client))
        all_results.append(_test_create_employee_invalid_email(client))
        all_results.append(_test_create_employee_invalid_department(client))
        all_results.append(_test_create_employee_duplicate_email(client))
        all_results.append(_test_create_employee_future_date(client))
        all_results.append(_test_create_employee_bad_date_format(client))

        _section("PHASE 3 - Tests: GET Employee(s)")
        all_results.append(_test_get_all_employees(client))
        all_results.append(_test_get_employee_by_id_success(client))
        all_results.append(_test_get_employee_by_id_not_found(client, "99999999-9999-9999-9999-999999999999"))

        _section("PHASE 3 - Tests: UPDATE Employee (HTTP -> Pydantic -> DB)")
        all_results.append(_test_update_employee_success(client))
        all_results.append(_test_update_employee_not_found(client))
        all_results.append(_test_update_employee_invalid_name(client))
        all_results.append(_test_update_employee_duplicate_email(client))

        _section("PHASE 3 - Tests: DELETE Employee")
        all_results.append(_test_delete_employee_success(client))
        all_results.append(_test_delete_employee_not_found(client))
        
        _section("PHASE 3 - Tests: Verify DELETE")
        all_results.append(_test_get_employee_by_id_not_found(client, "11111111-1111-1111-1111-111111111111"))

    # ============================================================
    # PHASE 4: DOWN Migration (Cleanup)
    # ============================================================
    _section("PHASE 4 - DOWN Migration (tests/migrations/test_down.sql)")
    _run_migration(master_engine, down_sql, "DOWN migration on TEST MASTER")
    time.sleep(1)

    total  = len(all_results)
    passed = sum(1 for r in all_results if r)
    failed = total - passed

    _banner("TEST RESULTS SUMMARY")
    print(f"  Total : {BOLD}{total}{RESET}")
    print(f"  Passed: {GREEN}{BOLD}{passed}{RESET}")
    print(f"  Failed: {RED}{BOLD}{failed}{RESET}")

    if failed == 0:
        print(f"\n  {GREEN}{BOLD}>>> ALL TESTS PASSED <<<{RESET}\n")
    else:
        print(f"\n  {RED}{BOLD}!!! {failed} TEST(S) FAILED !!!{RESET}\n")

    master_engine.dispose()
    replica_engine.dispose()

    return 0 if failed == 0 else 1
