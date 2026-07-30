from app.models.user import User, db

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

def test_login_by_roll_no(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "STU001",
            "password": "student123"
        }
    )
    assert response.status_code == 200
    assert "token" in response.get_json()

def test_login_by_employee_id(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "FAC001",
            "password": "faculty123"
        }
    )
    assert response.status_code == 200
    assert "token" in response.get_json()

def test_login_missing_fields(client):
    response = client.post(
        "/api/auth/login",
        json={}
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Email/Register Number and Password are required"

def test_login_invalid_password(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "rahul@allclub.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid email/register number or password"

def test_login_non_existent_user(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "doesnotexist@allclub.com",
            "password": "password"
        }
    )
    assert response.status_code == 401

def test_login_deactivated_user(client, app):
    with app.app_context():
        user = User.query.filter_by(email="rahul@allclub.com").first()
        user.account_status = "DEACTIVATED"
        db.session.commit()

    response = client.post(
        "/api/auth/login",
        json={
            "email": "rahul@allclub.com",
            "password": "student123"
        }
    )
    assert response.status_code == 403
    assert response.get_json()["error"] == "Your account has been deactivated. Please contact admin."

def test_register_student_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "fullName": "John Doe",
            "email": "johndoe@example.com",
            "password": "securepassword",
            "phone": "+91 98765 43210",
            "role": "STUDENT",
            "registerNumber": "STU999",
            "year": "2nd Year"
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "token" in data
    assert data["user"]["email"] == "johndoe@example.com"
    assert data["user"]["role"] == "STUDENT"

def test_register_faculty_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "fullName": "Dr. Jane Doe",
            "email": "janedoe@example.com",
            "password": "securepassword",
            "phone": "+91 98765 43211",
            "role": "FACULTY",
            "registerNumber": "FAC999",
            "designation": "Professor"
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "token" in data
    assert data["user"]["email"] == "janedoe@example.com"
    assert data["user"]["role"] == "FACULTY"

def test_register_missing_fields(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "missingname@example.com",
            "password": "securepassword"
        }
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Full Name, Email, and Password are required"

def test_register_duplicate_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "fullName": "Rahul Duplicate",
            "email": "rahul@allclub.com",
            "password": "securepassword"
        }
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "A user with this email already exists"

def test_register_duplicate_roll_no(client):
    response = client.post(
        "/api/auth/register",
        json={
            "fullName": "Another Rahul",
            "email": "anotherrahul@example.com",
            "password": "securepassword",
            "role": "STUDENT",
            "registerNumber": "STU001"
        }
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Register/Roll number already exists"

def test_register_duplicate_employee_id(client):
    response = client.post(
        "/api/auth/register",
        json={
            "fullName": "Another Meena",
            "email": "anothermeena@example.com",
            "password": "securepassword",
            "role": "FACULTY",
            "registerNumber": "FAC001"
        }
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Employee ID already exists"

def test_logout(client, student_headers):
    # Verify we are logged in
    res = client.get("/api/auth/me", headers=student_headers)
    assert res.status_code == 200

    # Logout
    res_logout = client.post("/api/auth/logout", headers=student_headers)
    assert res_logout.status_code == 200

    # Trying to access /me after logout should return 401
    res_me_again = client.get("/api/auth/me", headers=student_headers)
    assert res_me_again.status_code == 401

def test_change_password(client):
    temp_user_data = {
        "fullName": "Temp User",
        "email": "temp@example.com",
        "password": "old_password123",
        "phone": "+91 99999 88888",
        "role": "STUDENT",
        "registerNumber": "TEMP001",
        "year": "1st Year"
    }
    reg_res = client.post("/api/auth/register", json=temp_user_data)
    assert reg_res.status_code == 201
    token = reg_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Change password
    change_res = client.post(
        "/api/auth/change-password",
        headers=headers,
        json={
            "oldPassword": "old_password123",
            "newPassword": "new_password123"
        }
    )
    assert change_res.status_code == 200

    # Try logging in with the old password - should fail
    login_fail_res = client.post(
        "/api/auth/login",
        json={
            "email": "temp@example.com",
            "password": "old_password123"
        }
    )
    assert login_fail_res.status_code == 401

    # Try logging in with the new password - should succeed
    login_success_res = client.post(
        "/api/auth/login",
        json={
            "email": "temp@example.com",
            "password": "new_password123"
        }
    )
    assert login_success_res.status_code == 200

def test_change_password_failures(client, student_headers):
    # Missing fields
    res = client.post("/api/auth/change-password", headers=student_headers, json={})
    assert res.status_code == 400

    # Incorrect current password
    res = client.post(
        "/api/auth/change-password",
        headers=student_headers,
        json={
            "oldPassword": "wrong_password",
            "newPassword": "new_password123"
        }
    )
    assert res.status_code == 400

def test_get_me(client, student_headers):
    res = client.get("/api/auth/me", headers=student_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["email"] == "rahul@allclub.com"