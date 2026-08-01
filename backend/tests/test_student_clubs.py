AI_CLUB = 1
MUSIC_CLUB = 2
SPORTS_CLUB = 3
PHOTOGRAPHY_CLUB = 5
INVALID_CLUB = 999

def test_get_clubs(client, student_headers):
    response = client.get(
        "/api/student/clubs",
        headers=student_headers
    )

    assert response.status_code == 200

    clubs = response.get_json()

    assert isinstance(clubs, list)
    assert len(clubs) == 8

    ai_club = clubs[0]

    assert ai_club["id"] == 1
    assert ai_club["name"] == "AI Club"
    assert ai_club["category"] == "Technology"
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
    assert len(clubs) == 7

    club = clubs[0]

    assert club["id"] == 1
    assert club["name"] == "AI Club"
    assert club["membershipRole"] == "MEMBER"
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

    assert len(clubs) == 8
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

    assert len(clubs) == 6

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
        f"/api/student/clubs/{MUSIC_CLUB}/join",
        headers=admin_headers
    )

    assert response.status_code == 403

def test_faculty_cannot_join_club(client, faculty_headers):
    response = client.post(
        f"/api/student/clubs/{MUSIC_CLUB}/join",
        headers=faculty_headers
    )

    assert response.status_code == 403

def test_unauthenticated_request(client):
    response = client.post(
        f"/api/student/clubs/{MUSIC_CLUB}/join"
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Authorization header is missing"

def test_invalid_token(client):
    response = client.post(
        f"/api/student/clubs/{MUSIC_CLUB}/join",
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
    
    photography_club = clubs[4]
    assert photography_club["id"] == PHOTOGRAPHY_CLUB

    assert photography_club["activeMembers"] == 2
    assert photography_club["totalMembers"] == 2

# Club Events
def test_get_club_events(client, student_headers):
    response = client.get(
        f"/api/student/clubs/{AI_CLUB}/events",
        headers=student_headers
    )

    assert response.status_code == 200

    events = response.get_json()

    assert isinstance(events, list)
    assert len(events) == 1

    event = next(
            e for e in events
            if e["id"] == 1
        )

    assert event["id"] == 1
    assert event["name"] == "AI Hack Sprint"
    assert event["status"] == "LIVE"

    assert event["venueName"] == "Innovation Lab"

def test_get_invalid_club_events(client, student_headers):
    response = client.get(
        f"/api/student/clubs/{INVALID_CLUB}/events",
        headers=student_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_get_club_events_not_empty(client, student_headers):
    response = client.get(
        f"/api/student/clubs/{SPORTS_CLUB}/events",
        headers=student_headers
    )

    assert response.status_code == 200

    events = response.get_json()

    assert events != []

# Club Members
def test_get_club_members(client, student_headers):
    response = client.get(
        f"/api/student/clubs/{AI_CLUB}/members",
        headers=student_headers
    )

    assert response.status_code == 200

    members = response.get_json()

    assert isinstance(members, list)
    assert len(members) == 3

    member = next(
        m for m in members
        if m["email"] == "rahul@allclub.com"
    )

    assert member["id"] == 6
    assert member["name"] == "Rahul Sharma"
    assert member["email"] == "rahul@allclub.com"

    assert member["membershipRole"] == "MEMBER"
    assert member["membershipStatus"] == "ACTIVE"

def test_get_invalid_club_members(client, student_headers):
    response = client.get(
        f"/api/student/clubs/{INVALID_CLUB}/members",
        headers=student_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

