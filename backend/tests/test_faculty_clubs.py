AI_CLUB = 1
MUSIC_CLUB = 2
SPORTS_CLUB = 3
INVALID_CLUB = 999
RAHUL_USER_ID = 6

# Club Management
def test_get_clubs(client, faculty_headers):
    response = client.get(
        "/api/faculty/clubs",
        headers=faculty_headers
    )

    assert response.status_code == 200

    clubs = response.get_json()

    assert isinstance(clubs, list)
    assert len(clubs) == 8

    ai_club = next(
        c for c in clubs
        if c["name"] == "AI Club"
    )

    assert ai_club["id"] == AI_CLUB
    assert ai_club["name"] == "AI Club"
    assert ai_club["category"] == "Technology"
    assert ai_club["status"] == "ACTIVE"

    assert ai_club["activeMembers"] == 1
    assert ai_club["totalMembers"] == 1

    assert len(ai_club["faculty"]) == 1
    assert ai_club["faculty"][0]["name"] == "Dr. Meena Rao"

    assert len(ai_club["organizers"]) == 1
    assert ai_club["organizers"][0]["name"] == "Rahul Sharma"

# Club Administration
def test_edit_club(client, faculty_headers):
    response = client.put(
        f"/api/faculty/clubs/{AI_CLUB}/edit",
        headers=faculty_headers,
        json={
            "name": "Artificial Intelligence Club",
            "description": "Updated description.",
            "category": "Technology",
            "facultyCoordinatorIds": [2]
        }
    )

    print(response.get_json())

    assert response.status_code == 200

    club = response.get_json()

    assert club["id"] == AI_CLUB
    assert club["name"] == "Artificial Intelligence Club"
    assert club["description"] == "Updated description."
    assert club["category"] == "Technology"

    response = client.get(
        "/api/faculty/clubs",
        headers=faculty_headers
    )

    assert response.status_code == 200

    club = next(c for c in response.get_json() if c["id"] == AI_CLUB)

    assert club["name"] == "Artificial Intelligence Club"
    assert club["description"] == "Updated description."
    assert club["category"] == "Technology"

def test_edit_invalid_club(client, faculty_headers):
    response = client.put(
        f"/api/faculty/clubs/{INVALID_CLUB}/edit",
        headers=faculty_headers,
        json={
            "name": "Updated Club",
            "description": "Updated description.",
            "category": "Technology",
            "facultyCoordinatorIds": [2]
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_edit_invalid_category(client, faculty_headers):
    response = client.put(
        f"/api/faculty/clubs/{AI_CLUB}/edit",
        headers=faculty_headers,
        json={
            "name": "AI Club",
            "description": "Updated description.",
            "category": "Gaming",
            "facultyCoordinatorIds": [2]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Invalid category."

# Club Members
def test_get_club_members(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{AI_CLUB}/members",
        headers=faculty_headers
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

def test_get_invalid_club_members(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{INVALID_CLUB}/members",
        headers=faculty_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_get_club_members_includes_inactive(client, faculty_headers):
    response = client.patch(
        f"/api/faculty/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=faculty_headers
    )

    assert response.status_code == 200

    response = client.get(
        f"/api/faculty/clubs/{AI_CLUB}/members",
        headers=faculty_headers
    )

    assert response.status_code == 200

    members = response.get_json()

    assert len(members) == 3
    assert members[0]["membershipStatus"] == "INACTIVE"

def test_get_club_member(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}",
        headers=faculty_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["id"] == RAHUL_USER_ID
    assert member["rollNumber"] == "STU001"
    assert member["name"] == "Rahul Sharma"
    assert member["email"] == "rahul@allclub.com"
    assert member["phoneNumber"] == "+91 90000 00003"

    assert member["department"] == "Computer Science"
    assert member["yearOfStudy"] == "3rd Year"

    assert member["membershipRole"] == "MEMBER"
    assert member["membershipStatus"] == "ACTIVE"

def test_get_club_member_invalid_club(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{INVALID_CLUB}/members/{RAHUL_USER_ID}",
        headers=faculty_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_get_invalid_club_member(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{AI_CLUB}/members/999",
        headers=faculty_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Member not found"

def test_deactivate_club_member(client, faculty_headers):
    response = client.patch(
        f"/api/faculty/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=faculty_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["id"] == RAHUL_USER_ID
    assert member["membershipStatus"] == "INACTIVE"

    response = client.get(
        f"/api/faculty/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}",
        headers=faculty_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["membershipStatus"] == "INACTIVE"

def test_duplicate_deactivate_club_member(client, faculty_headers):
    response = client.patch(
        f"/api/faculty/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=faculty_headers
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/faculty/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=faculty_headers
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Member is already inactive."

def test_deactivate_club_member_invalid_club(client, faculty_headers):
    response = client.patch(
        f"/api/faculty/clubs/{INVALID_CLUB}/members/1/deactivate",
        headers=faculty_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_deactivate_invalid_club_member(client, faculty_headers):
    response = client.patch(
        f"/api/faculty/clubs/{AI_CLUB}/members/999/deactivate",
        headers=faculty_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Member not found"

# Club Events
def test_get_club_events(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{AI_CLUB}/events",
        headers=faculty_headers
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

def test_get_invalid_club_events(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{INVALID_CLUB}/events",
        headers=faculty_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_get_club_events_not_empty(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{SPORTS_CLUB}/events",
        headers=faculty_headers
    )

    assert response.status_code == 200

    events = response.get_json()

    assert events != []

# Authorization
def test_unauthenticated_request(client):
    response = client.get(
        f"/api/faculty/clubs"
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Authorization header is missing"

def test_invalid_token(client):
    response = client.get(
        f"/api/faculty/clubs",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Not enough segments"

def test_edit_other_faculty_club_forbidden(client, faculty_headers):
    response = client.put(
        "/api/faculty/clubs/2/edit",
        headers=faculty_headers,
        json={
            "name": "Music Club",
            "description": "Updated description",
            "category": "CULTURAL"
        }
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == "You are not assigned to this club."

def test_deactivate_other_faculty_member_forbidden(
    client,
    faculty_headers
):
    response = client.patch(
        "/api/faculty/clubs/2/members/14/deactivate",
        headers=faculty_headers
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == "You are not assigned to this club."

