def test_get_user_assignments(client, student_headers):
    # Rahul Sharma user_id is 6 in seeded db
    response = client.get(
        "/api/assignment-tickets/user/6",
        headers=student_headers
    )
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["success"] is True
    assert "data" in res_data
    assert "active" in res_data["data"]
    assert "history" in res_data["data"]


def test_get_user_assignments_unauthorized(client, student_headers):
    # Rahul (user_id 6) attempts to access another user's assignments (user_id 3)
    response = client.get(
        "/api/assignment-tickets/user/3",
        headers=student_headers
    )
    assert response.status_code == 403


def test_create_role_request(client, student_headers):
    payload = {
        "requestType": "BECOME_ORGANIZER",
        "title": "Request to join AI Club as Organizer",
        "description": "Interested in leading tech workshops.",
        "priority": "MEDIUM",
        "referenceType": "CLUB",
        "referenceId": 1,
        "referenceName": "AI Club"
    }
    response = client.post(
        "/api/requests",
        json=payload,
        headers=student_headers
    )
    assert response.status_code == 201
    res_data = response.get_json()
    assert res_data["success"] is True
    assert res_data["data"]["requestType"] == "BECOME_ORGANIZER"
    assert len(res_data["data"]["approvals"]) >= 1


def test_student_leave_assignment_ticket(client, student_headers):
    # First fetch assignments to get an active ticket id
    res = client.get("/api/assignment-tickets/user/6", headers=student_headers).get_json()
    active_tickets = res["data"]["active"]
    if active_tickets:
        ticket_id = active_tickets[0]["id"]
        response = client.post(
            f"/api/assignment-tickets/{ticket_id}/leave",
            headers=student_headers
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "Successfully left role."


def test_student_leave_assignment_invalid_id(client, student_headers):
    response = client.post(
        "/api/assignment-tickets/999/leave",
        headers=student_headers
    )
    assert response.status_code == 404
