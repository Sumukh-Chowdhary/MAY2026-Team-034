def test_get_user_profile(client, faculty_headers):
    # Faculty user meena@allclub.com is ID 3
    response = client.get(
        "/api/users/3",
        headers=faculty_headers
    )
    assert response.status_code == 200
    user_data = response.get_json()
    assert "email" in user_data
    assert user_data["email"] == "meena@allclub.com"


def test_update_self_profile(client, faculty_headers):
    payload = {
        "fullName": "Dr. Meena Rao Updated",
        "phone": "+91 99999 88888",
        "designation": "Senior Professor",
        "bio": "Updated bio statement for testing."
    }
    response = client.put(
        "/api/users/3",
        json=payload,
        headers=faculty_headers
    )
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data["fullName"] == "Dr. Meena Rao Updated"
    assert user_data["phone"] == "+91 99999 88888"


def test_update_other_user_profile_forbidden(client, student_headers):
    # Student (user_id 6) attempts to update Faculty (user_id 3)
    payload = {
        "fullName": "Hacked Name"
    }
    response = client.put(
        "/api/users/3",
        json=payload,
        headers=student_headers
    )
    assert response.status_code == 403


def test_admin_update_any_user_profile(client, admin_headers):
    payload = {
        "fullName": "Rahul Sharma (Admin Verified)",
        "accountStatus": "ACTIVE"
    }
    response = client.put(
        "/api/users/6",
        json=payload,
        headers=admin_headers
    )
    assert response.status_code == 200
    user_data = response.get_json()
    assert user_data["fullName"] == "Rahul Sharma (Admin Verified)"

def test_get_user_profile_requires_auth(client):
    response = client.get("/api/users/3")

    assert response.status_code == 401

def test_get_nonexistent_user_profile(client, faculty_headers):
    response = client.get(
        "/api/users/999",
        headers=faculty_headers
    )

    assert response.status_code == 404

def test_student_can_view_faculty_profile(client, student_headers):
    response = client.get(
        "/api/users/3",
        headers=student_headers
    )

    assert response.status_code == 200

    user_data = response.get_json()
    assert user_data["email"] == "meena@allclub.com"

def test_faculty_profile_contains_profile_fields(client, faculty_headers):
    response = client.get("/api/users/3", headers=faculty_headers)

    assert response.status_code == 200

    user_data = response.get_json()
    print(user_data)

    assert user_data["role"] == "FACULTY"
    assert "fullName" in user_data
    assert "phone" in user_data
    assert "department" in user_data
    assert "bio" in user_data
    assert "avatarStyle" in user_data
    assert "avatarSeed" in user_data

def test_student_profile_contains_profile_fields(client, student_headers):
    response = client.get(
        "/api/users/6",
        headers=student_headers
    )

    assert response.status_code == 200

    user_data = response.get_json()

    assert user_data["role"] == "STUDENT"
    assert "fullName" in user_data
    assert "phone" in user_data
    assert "registerNumber" in user_data
    assert "department" in user_data
    assert "year" in user_data
    assert "bio" in user_data
    assert "avatarStyle" in user_data
    assert "avatarSeed" in user_data

