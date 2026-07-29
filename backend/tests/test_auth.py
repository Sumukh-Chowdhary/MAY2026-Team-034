STUDENT = {
    "email": "rahul@allclub.com",
    "password": "student123"
}

FACULTY = {
    "email": "meena@allclub.com",
    "password": "faculty123"
}

ADMIN = {
    "email": "admin@allclub.com",
    "password": "admin123"
}

def test_admin_login(client):
    response = client.post(
        "/api/auth/login",
        json=ADMIN
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "token" in data

def test_faculty_login(client):
    response = client.post(
        "/api/auth/login",
        json=FACULTY
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "token" in data

def test_student_login(client):
    response = client.post(
        "/api/auth/login",
        json=STUDENT
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "token" in data