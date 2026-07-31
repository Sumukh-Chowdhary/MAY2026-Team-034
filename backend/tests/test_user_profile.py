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
