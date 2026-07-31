import os
import tempfile

import pytest

from app import create_app
from app.models.user import db
from app.utils.seed import seed_database
from config import Config


@pytest.fixture
def app():

    db_fd, db_path = tempfile.mkstemp()

    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    app = create_app(TestConfig)

    seed_database(app)

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    os.close(db_fd)
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
            "email": "rahul@allclub.com",
            "password": "student123"
        }
    )

    assert response.status_code == 200

    token = response.get_json()["token"]

    return {
        "Authorization": f"Bearer {token}"
    }