import os
import tempfile
import shutil
import sys

# Ensure backend directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from unittest.mock import patch

from app import create_app
from app.models.user import db
from app.utils.seed import seed_database
from config import Config


@pytest.fixture(autouse=True)
def mock_kafka():
    with patch("app.kafka.producer.publish_event", return_value={"published": False, "partition": 0, "offset": 0}):
        yield


@pytest.fixture(scope="session")
def template_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    class TemplateConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{path}"

    app = create_app(TemplateConfig)
    seed_database(app)

    with app.app_context():
        db.session.remove()
        db.engine.dispose()

    yield path

    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def app(template_db):
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    shutil.copyfile(template_db, db_path)

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    app = create_app(TestConfig)

    yield app

    with app.app_context():
        db.session.remove()
        db.engine.dispose()

    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_headers(client):

    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@allclub.com",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    token = response.get_json()["token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def faculty_headers(client):

    response = client.post(
        "/api/auth/login",
        json={
            "email": "meena@allclub.com",
            "password": "faculty123"
        }
    )

    assert response.status_code == 200

    token = response.get_json()["token"]

    return {
        "Authorization": f"Bearer {token}"
    }

@pytest.fixture
def student_headers(client):

    response = client.post(
        "/api/auth/login",
        json={
            "username": "Y24CS001",
            "password": "student123"
        }
    )

    assert response.status_code == 200

    token = response.get_json()["token"]

    return {
        "Authorization": f"Bearer {token}"
    }