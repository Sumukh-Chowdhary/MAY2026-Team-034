def test_get_my_supervised_clubs(client, faculty_headers):
    response = client.get(
        "/api/faculty/my-clubs",
        headers=faculty_headers
    )
    assert response.status_code == 200
    clubs = response.get_json()
    assert isinstance(clubs, list)
    assert len(clubs) >= 1
    
    club = clubs[0]
    assert "clubName" in club
    assert "roleTitle" in club
    assert "assignedStudents" in club
    assert "events" in club


def test_get_my_supervised_clubs_unauthorized(client, student_headers):
    response = client.get(
        "/api/faculty/my-clubs",
        headers=student_headers
    )
    assert response.status_code == 403


def test_faculty_requests_dashboard(client, faculty_headers):
    response = client.get(
        "/api/faculty/requests/dashboard",
        headers=faculty_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "data" in data
    assert "myTickets" in data["data"]
    assert "incomingRequests" in data["data"]


def test_leave_faculty_role(client, faculty_headers):
    # Faculty leaves AI Club (ID 1)
    response = client.post(
        "/api/faculty/clubs/1/leave",
        headers=faculty_headers
    )
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["message"] == "Stepped down from club coordinator role successfully."

    # Verify no longer listed in supervised clubs
    my_clubs = client.get("/api/faculty/my-clubs", headers=faculty_headers).get_json()
    assert not any(c["id"] == 1 for c in my_clubs)


def test_leave_faculty_role_invalid_club(client, faculty_headers):
    response = client.post(
        "/api/faculty/clubs/999/leave",
        headers=faculty_headers
    )
    assert response.status_code == 404
