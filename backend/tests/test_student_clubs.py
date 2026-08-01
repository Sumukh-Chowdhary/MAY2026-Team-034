AI_CLUB = 1
ROBOTICS_CLUB = 2
PHOTOGRAPHY_CLUB = 3
SPORTS_CLUB = 4
INVALID_CLUB = 999

def test_get_clubs(client, student_headers):
    response = client.get(
        "/api/student/clubs",
        headers=student_headers
    )

    assert response.status_code == 200

    clubs = response.get_json()

    assert isinstance(clubs, list)
    assert len(clubs) >= 4

    ai_club = clubs[0]

    assert ai_club["id"] == 1
    assert ai_club["name"] == "Coding Club"
    assert ai_club["category"] == "TECHNICAL"
    assert ai_club["status"] == "ACTIVE"
    assert ai_club["activeMembers"] == 1
    assert ai_club["totalMembers"] == 1

    assert len(ai_club["faculty"]) == 1
    assert ai_club["faculty"][0]["name"] == "Dr. Meena Rao"

    assert len(ai_club["organizers"]) == 1
    assert ai_club["organizers"][0]["name"] == "Rahul Sharma"

def test_get_my_clubs(client, student_headers):
    response = client.get(
        "/api/student/my-clubs",
        headers=student_headers
    )

    assert response.status_code == 200

    clubs = response.get_json()

    assert isinstance(clubs, list)
    assert len(clubs) == 2

    club = clubs[0]

    assert club["id"] == 1
    assert club["name"] == "Coding Club"
    assert club["status"] == "ACTIVE"

def test_join_club(client, student_headers):
    response = client.post(
        f"/api/student/clubs/{PHOTOGRAPHY_CLUB}/join",
        headers=student_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["clubId"] == PHOTOGRAPHY_CLUB
    assert data["message"] == "Joined club successfully"

    response = client.get(
        "/api/student/my-clubs",
        headers=student_headers
    )

    clubs = response.get_json()

    assert len(clubs) == 3
    assert any(club["id"] == PHOTOGRAPHY_CLUB for club in clubs)

def test_leave_club(client, student_headers):
    response = client.post(
        f"/api/student/clubs/{AI_CLUB}/leave",
        headers=student_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["clubId"] == AI_CLUB

    response = client.get(
        "/api/student/my-clubs",
        headers=student_headers
    )

    clubs = response.get_json()

    assert len(clubs) == 1

def test_duplicate_leave_club(client, student_headers):
    response = client.post(
        f"/api/student/clubs/{AI_CLUB}/leave",
        headers=student_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["clubId"] == AI_CLUB

    response = client.post(
            f"/api/student/clubs/{AI_CLUB}/leave",
            headers=student_headers
    )

    assert response.status_code == 409

def test_invalid_join_club(client, student_headers):
    response = client.post(
        f"/api/student/clubs/{INVALID_CLUB}/join",
        headers=student_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_invalid_leave_club(client, student_headers):
    response = client.post(
        f"/api/student/clubs/{INVALID_CLUB}/leave",
        headers=student_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_admin_cannot_join_club(client, admin_headers):
    response = client.post(
        f"/api/student/clubs/{ROBOTICS_CLUB}/join",
        headers=admin_headers
    )

    assert response.status_code == 403

def test_faculty_cannot_join_club(client, faculty_headers):
    response = client.post(
        f"/api/student/clubs/{ROBOTICS_CLUB}/join",
        headers=faculty_headers
    )

    assert response.status_code == 403

def test_unauthenticated_request(client):
    response = client.post(
        f"/api/student/clubs/{ROBOTICS_CLUB}/join"
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Authorization header is missing"

def test_invalid_token(client):
    response = client.post(
        f"/api/student/clubs/{ROBOTICS_CLUB}/join",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Not enough segments"

def test_incremented_membercounts(client, student_headers):
    response = client.post(
        f"/api/student/clubs/{PHOTOGRAPHY_CLUB}/join",
        headers=student_headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["clubId"] == PHOTOGRAPHY_CLUB
    assert data["message"] == "Joined club successfully"

    response = client.get(
        "/api/student/clubs",
        headers=student_headers
    )

    clubs = response.get_json()
    
    assert isinstance(clubs, list)
    
    photo_club = next(c for c in clubs if c["id"] == PHOTOGRAPHY_CLUB)
    assert photo_club["id"] == PHOTOGRAPHY_CLUB

    assert photo_club["activeMembers"] == 2
    assert photo_club["totalMembers"] == 2
