AI_CLUB = 1
MUSIC_CLUB = 2
SPORTS_CLUB = 3
INVALID_CLUB = 999
RAHUL_USER_ID = 6

# Club Management
def test_get_clubs(client, admin_headers):
    response = client.get(
        "/api/admin/clubs",
        headers=admin_headers
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

    assert ai_club["activeMembers"] == 3
    assert ai_club["totalMembers"] == 3

    assert len(ai_club["faculty"]) == 1
    assert ai_club["faculty"][0]["name"] == "Dr. Meena Rao"

    assert len(ai_club["organizers"]) == 1
    assert ai_club["organizers"][0]["name"] == "Rahul Sharma"

def test_update_club_status(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{MUSIC_CLUB}/status",
        headers=admin_headers,
        json={"status": "INACTIVE"}
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "INACTIVE"

def test_update_invalid_club_status(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{INVALID_CLUB}/status",
        headers=admin_headers,
        json={"status": "INACTIVE"}
    )

    assert response.status_code == 404

# Club Administration
def test_create_club(client, admin_headers):
    response = client.post(
        "/api/admin/clubs/create",
        headers=admin_headers,
        json={
            "name": "Chess Club",
            "description": "Club for chess enthusiasts.",
            "category": "Academic",
            "facultyCoordinatorIds": [2]
        }
    )

    print(response.get_json())

    assert response.status_code == 201

    club = response.get_json()

    assert club["name"] == "Chess Club"
    assert club["description"] == "Club for chess enthusiasts."
    assert club["category"] == "Academic"
    assert club["status"] == "ACTIVE"

    assert club["activeMembers"] == 0
    assert club["totalMembers"] == 0

    response = client.get(
        "/api/admin/clubs",
        headers=admin_headers
    )

    assert response.status_code == 200

    clubs = response.get_json()

    assert len(clubs) == 9

    assert any(
        c["name"] == "Chess Club"
        for c in clubs
    )

def test_create_club_invalid_category(client, admin_headers):
    response = client.post(
        "/api/admin/clubs/create",
        headers=admin_headers,
        json={
            "name": "Chess Club",
            "description": "Club for chess enthusiasts.",
            "category": "Gaming",
            "facultyCoordinatorIds": [2]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Invalid category."

def test_create_duplicate_club(client, admin_headers):
    response = client.post(
        "/api/admin/clubs/create",
        headers=admin_headers,
        json={
            "name": "AI Club",
            "description": "Duplicate",
            "category": "Technology",
            "facultyCoordinatorIds": [2]
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "A club with this name already exists."

def test_edit_club(client, admin_headers):
    response = client.put(
        f"/api/admin/clubs/{AI_CLUB}/edit",
        headers=admin_headers,
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
        "/api/admin/clubs",
        headers=admin_headers
    )

    assert response.status_code == 200

    club = next(c for c in response.get_json() if c["id"] == AI_CLUB)

    assert club["name"] == "Artificial Intelligence Club"
    assert club["description"] == "Updated description."
    assert club["category"] == "Technology"

def test_edit_invalid_club(client, admin_headers):
    response = client.put(
        f"/api/admin/clubs/{INVALID_CLUB}/edit",
        headers=admin_headers,
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

def test_edit_invalid_category(client, admin_headers):
    response = client.put(
        f"/api/admin/clubs/{AI_CLUB}/edit",
        headers=admin_headers,
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

def test_archive_club(client, admin_headers):
    response = client.delete(
        f"/api/admin/clubs/{MUSIC_CLUB}",
        headers=admin_headers
    )

    assert response.status_code == 200

    club = response.get_json()

    assert club["id"] == MUSIC_CLUB
    assert club["status"] == "INACTIVE"

    response = client.get(
        "/api/admin/clubs",
        headers=admin_headers
    )

    assert response.status_code == 200

    club = next(c for c in response.get_json() if c["id"] == MUSIC_CLUB)

    assert club["status"] == "INACTIVE"

def test_duplicate_archive_club(client, admin_headers):
    response = client.delete(
        f"/api/admin/clubs/{MUSIC_CLUB}",
        headers=admin_headers
    )

    assert response.status_code == 200

    response = client.delete(
        f"/api/admin/clubs/{MUSIC_CLUB}",
        headers=admin_headers
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Club is already inactive."

def test_archive_invalid_club(client, admin_headers):
    response = client.delete(
        f"/api/admin/clubs/{INVALID_CLUB}",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

# Faculty
def test_get_faculty(client, admin_headers):
    response = client.get(
        "/api/admin/clubs/faculty-details",
        headers=admin_headers
    )

    assert response.status_code == 200

    faculty = response.get_json()

    assert isinstance(faculty, list)
    assert len(faculty) == 4

    meena = next(
        f for f in faculty
        if f["name"] == "Dr. Meena Rao"
    )

    assert meena["designation"] == "Associate Professor"
    assert meena["department"] == "Computer Science"

# Admin Specific
def test_get_club_members(client, admin_headers):
    response = client.get(
        f"/api/admin/clubs/{AI_CLUB}/members",
        headers=admin_headers
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

def test_get_invalid_club_members(client, admin_headers):
    response = client.get(
        f"/api/admin/clubs/{INVALID_CLUB}/members",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_get_club_members_includes_inactive(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    response = client.get(
        f"/api/admin/clubs/{AI_CLUB}/members",
        headers=admin_headers
    )

    assert response.status_code == 200

    members = response.get_json()

    assert len(members) == 3
    assert members[0]["membershipStatus"] == "INACTIVE"

def test_get_club_member(client, admin_headers):
    response = client.get(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}",
        headers=admin_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["id"] == RAHUL_USER_ID
    assert member["rollNumber"] == "Y24CS001"
    assert member["name"] == "Rahul Sharma"
    assert member["email"] == "rahul@allclub.com"
    assert member["phoneNumber"] == "+91 90000 00003"

    assert member["department"] == "Computer Science"
    assert member["yearOfStudy"] == "3rd Year"

    assert member["membershipRole"] == "MEMBER"
    assert member["membershipStatus"] == "ACTIVE"

def test_get_club_member_invalid_club(client, admin_headers):
    response = client.get(
        f"/api/admin/clubs/{INVALID_CLUB}/members/{RAHUL_USER_ID}",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_get_invalid_club_member(client, admin_headers):
    response = client.get(
        f"/api/admin/clubs/{AI_CLUB}/members/999",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Member not found"

# Deactivate Club Member
def test_deactivate_club_member(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["id"] == RAHUL_USER_ID
    assert member["membershipStatus"] == "INACTIVE"

    response = client.get(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}",
        headers=admin_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["membershipStatus"] == "INACTIVE"

def test_duplicate_deactivate_club_member(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Member is already inactive."

def test_deactivate_club_member_invalid_club(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{INVALID_CLUB}/members/1/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_deactivate_invalid_club_member(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/999/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Member not found"

# Reactivate Club Member
def test_reactivate_club_member(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/reactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["id"] == RAHUL_USER_ID
    assert member["membershipStatus"] == "ACTIVE"

    response = client.get(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}",
        headers=admin_headers
    )

    assert response.status_code == 200

    member = response.get_json()

    assert member["membershipStatus"] == "ACTIVE"

def test_duplicate_reactivate_club_member(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/reactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/reactivate",
        headers=admin_headers
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Member is already active."

def test_reactivate_club_member_invalid_club(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/admin/clubs/{INVALID_CLUB}/members/{RAHUL_USER_ID}/reactivate",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_reactivate_invalid_club_member(client, admin_headers):
    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/{RAHUL_USER_ID}/deactivate",
        headers=admin_headers
    )

    assert response.status_code == 200

    response = client.patch(
        f"/api/admin/clubs/{AI_CLUB}/members/999/reactivate",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Member not found"

# Club Events
def test_get_club_events(client, admin_headers):
    response = client.get(
        f"/api/admin/clubs/{AI_CLUB}/events",
        headers=admin_headers
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
    assert event["status"] == "COMPLETED"

    assert event["venueName"] == "Innovation Lab"

def test_get_invalid_club_events(client, admin_headers):
    response = client.get(
        f"/api/admin/clubs/{INVALID_CLUB}/events",
        headers=admin_headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Club not found"

def test_get_club_events_not_empty(client, admin_headers):
    response = client.get(
        f"/api/admin/clubs/{SPORTS_CLUB}/events",
        headers=admin_headers
    )

    assert response.status_code == 200

    events = response.get_json()

    assert events != []

# Authorization
def test_student_cannot_archive_club(client, student_headers):
    response = client.delete(
        f"/api/admin/clubs/{MUSIC_CLUB}",
        headers=student_headers
    )

    assert response.status_code == 403

def test_faculty_cannot_archive_club(client, faculty_headers):
    response = client.delete(
        f"/api/admin/clubs/{MUSIC_CLUB}",
        headers=faculty_headers
    )

    assert response.status_code == 403

def test_unauthenticated_request(client):
    response = client.get(
        f"/api/admin/clubs"
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Authorization header is missing"

def test_invalid_token(client):
    response = client.get(
        f"/api/admin/clubs",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["error"] == "Not enough segments"

