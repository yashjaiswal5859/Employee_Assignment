import pytest
from app import create_app
from models import db


@pytest.fixture
def app():
    """Create and configure a test app"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def sample_employee():
    """Sample employee data"""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "department": "Engineering",
        "date_joined": "2024-01-15"
    }
