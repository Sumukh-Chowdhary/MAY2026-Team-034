import pytest

def test_student_registration_and_login_flow(client):
    # 1. Register a new student
    reg_response = client.post(
        "/api/auth/register",
        json={
            "fullName": "Test Integration Student",
            "email": "test_integration_student@allclub.com",
            "password": "password123",
            "phone": "+91 99999 99999",
            "role": "STUDENT",
            "registerNumber": "STU999",
            "year": "1st Year"
        }
    )
    assert reg_response.status_code == 201
    
    # 2. Login with the new student credentials
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_integration_student@allclub.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Access student club listing (authorized)
    student_clubs_resp = client.get("/api/student/clubs", headers=headers)
    assert student_clubs_resp.status_code == 200

    # 4. Access faculty supervised clubs (unauthorized -> should return 403 Forbidden)
    faculty_resp = client.get("/api/faculty/my-clubs", headers=headers)
    assert faculty_resp.status_code == 403


def test_faculty_registration_and_login_flow(client):
    # 1. Register a new faculty member
    reg_response = client.post(
        "/api/auth/register",
        json={
            "fullName": "Test Integration Faculty",
            "email": "test_integration_faculty@allclub.com",
            "password": "password123",
            "phone": "+91 88888 88888",
            "role": "FACULTY",
            "registerNumber": "FAC999"
        }
    )
    assert reg_response.status_code == 201
    
    # 2. Login with the new faculty credentials
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "test_integration_faculty@allclub.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Access faculty supervised clubs (authorized)
    faculty_resp = client.get("/api/faculty/my-clubs", headers=headers)
    assert faculty_resp.status_code == 200

    # 4. Access admin endpoints (unauthorized -> should return 403 Forbidden)
    admin_resp = client.get("/api/admin/clubs", headers=headers)
    assert admin_resp.status_code == 403
