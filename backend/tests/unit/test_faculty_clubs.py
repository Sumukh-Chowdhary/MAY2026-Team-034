AI_CLUB = 1
MUSIC_CLUB = 2
SPORTS_CLUB = 3
INVALID_CLUB = 999
RAHUL_USER_ID = 24
MEENA_FACULTY_ID = 4

# Club Management
def test_get_clubs(client, faculty_headers):
    response = client.get(
        "/api/faculty/clubs",
        headers=faculty_headers
    )

    assert response.status_code == 200

    clubs = response.get_json()

    assert isinstance(clubs, list)
    assert len(clubs) == 20

    ai_club = next(
        c for c in clubs
        if c["name"] == "AI Club"
    )

    assert ai_club["id"] == AI_CLUB
    assert ai_club["name"] == "AI Club"
    assert ai_club["category"] == "Technology"
    assert ai_club["status"] == "ACTIVE"

    assert ai_club["activeMembers"] >= 1
    assert ai_club["totalMembers"] >= 1

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
            "facultyCoordinatorIds": [MEENA_FACULTY_ID]
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
            "facultyCoordinatorIds": [MEENA_FACULTY_ID]
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
            "facultyCoordinatorIds": [MEENA_FACULTY_ID]
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
    assert len(members) >= 1

    member = next(
        m for m in members
        if m["id"] == RAHUL_USER_ID
    )

    assert member["id"] == RAHUL_USER_ID
    assert member["name"] == "Rahul Sharma"
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

    assert len(members) >= 1
    assert any(m["id"] == RAHUL_USER_ID and m["membershipStatus"] == "INACTIVE" for m in members)

def test_get_club_member(client, faculty_headers):
    response = client.get(
        f"/api/faculty/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}",
        headers=faculty_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["id"] == RAHUL_USER_ID
    assert member["rollNumber"] == "Y24CS001"
    assert member["name"] == "Rahul Sharma"
    assert "Computer Science" in member["department"]
    assert member["yearOfStudy"] == "3rd Year"
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
    assert len(events) >= 1

    event = next(
            e for e in events
            if "AI Hack Sprint" in e["name"]
        )

    assert "AI Hack Sprint" in event["name"]
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

def test_edit_other_faculty_club_forbidden(client, app, faculty_headers):
    with app.app_context():
        from app.models.club import Club, ClubFaculty
        assigned_club_ids = {cf.club_id for cf in ClubFaculty.query.filter_by(faculty_id=MEENA_FACULTY_ID).all()}
        unassigned_club = Club.query.filter(~Club.id.in_(assigned_club_ids)).first()
        target_club_id = unassigned_club.id if unassigned_club else 99

    response = client.put(
        f"/api/faculty/clubs/{target_club_id}/edit",
        headers=faculty_headers,
        json={
            "name": "Music Club",
            "description": "Updated description",
            "category": "Cultural",
            "facultyCoordinatorIds": [MEENA_FACULTY_ID]
        }
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == "You are not assigned to this club."

def test_deactivate_other_faculty_member_forbidden(
    client,
    app,
    faculty_headers
):
    with app.app_context():
        from app.models.club import Club, ClubFaculty
        assigned_club_ids = {cf.club_id for cf in ClubFaculty.query.filter_by(faculty_id=MEENA_FACULTY_ID).all()}
        unassigned_club = Club.query.filter(~Club.id.in_(assigned_club_ids)).first()
        target_club_id = unassigned_club.id if unassigned_club else 99

    response = client.patch(
        f"/api/faculty/clubs/{target_club_id}/members/{RAHUL_USER_ID}/deactivate",
        headers=faculty_headers
    )

    assert response.status_code == 403

    data = response.get_json()

    assert data["error"] == "You are not assigned to this club."

