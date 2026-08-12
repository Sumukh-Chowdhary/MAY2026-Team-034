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


def test_phone_privacy_matrix(client, admin_headers, faculty_headers, student_headers):
    # Ensure student 6 has phone number set for test
    client.put("/api/users/6", json={"phone": "+91 98765 43210"}, headers=admin_headers)
    # Ensure faculty 3 has phone number set for test
    client.put("/api/users/3", json={"phone": "+91 91234 56789"}, headers=admin_headers)

    # 1. ADMIN viewing Student (6) -> Phone visible
    res = client.get("/api/users/6", headers=admin_headers)
    assert res.status_code == 200
    assert res.get_json()["phone"] == "+91 98765 43210"

    # 2. ADMIN viewing Faculty (3) -> Phone visible
    res = client.get("/api/users/3", headers=admin_headers)
    assert res.status_code == 200
    assert res.get_json()["phone"] == "+91 91234 56789"

    # 3. FACULTY viewing Student (6) -> Phone visible
    res = client.get("/api/users/6", headers=faculty_headers)
    assert res.status_code == 200
    assert res.get_json()["phone"] == "+91 98765 43210"

    # 4. FACULTY viewing Faculty (3) -> Phone visible (own/faculty)
    res = client.get("/api/users/3", headers=faculty_headers)
    assert res.status_code == 200
    assert res.get_json()["phone"] == "+91 91234 56789"

    # 5. STUDENT (6) viewing ANOTHER Student / Faculty (3) -> Phone NOT visible (None)
    res = client.get("/api/users/3", headers=student_headers)
    assert res.status_code == 200
    assert res.get_json()["phone"] is None

    # 6. STUDENT (6) viewing OWN profile (6) -> Phone IS visible
    res = client.get("/api/users/6", headers=student_headers)
    assert res.status_code == 200
    assert res.get_json()["phone"] == "+91 98765 43210"

