# Sprint 2 – Faculty new-endpoint tests
# Covers endpoints that had NO tests in Sprint 1:
#   GET  /api/faculty/my-clubs
#   POST /api/faculty/clubs/<id>/leave
#   GET  /api/faculty/general-events

AI_CLUB     = 1
INVALID_CLUB = 999


# ---------------------------------------------------------------------------
# GET /api/faculty/my-clubs
# ---------------------------------------------------------------------------

def test_faculty_my_clubs_returns_list(client, faculty_headers):
    """Faculty gets a list of clubs they supervise."""
    response = client.get('/api/faculty/my-clubs', headers=faculty_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_faculty_my_clubs_contains_ai_club(client, faculty_headers):
    """Dr. Meena Rao is seeded as faculty for AI Club — must appear."""
    response = client.get('/api/faculty/my-clubs', headers=faculty_headers)
    assert response.status_code == 200
    clubs = response.get_json()
    club_names = [c['clubName'] for c in clubs]
    assert 'AI Club' in club_names


def test_faculty_my_clubs_structure(client, faculty_headers):
    """Each club entry must include required fields."""
    response = client.get('/api/faculty/my-clubs', headers=faculty_headers)
    assert response.status_code == 200
    clubs = response.get_json()
    assert len(clubs) > 0
    for club in clubs:
        assert 'id' in club
        assert 'clubName' in club
        assert 'status' in club
        assert 'memberCount' in club


def test_faculty_my_clubs_unauthenticated(client):
    """Unauthenticated access returns 401."""
    response = client.get('/api/faculty/my-clubs')
    assert response.status_code == 401


def test_faculty_my_clubs_student_cannot_access(client, student_headers):
    """Student must receive 403 (role guard)."""
    response = client.get('/api/faculty/my-clubs', headers=student_headers)
    assert response.status_code == 403


def test_faculty_my_clubs_admin_cannot_access(client, admin_headers):
    """Admin must receive 403 (route is faculty-only)."""
    response = client.get('/api/faculty/my-clubs', headers=admin_headers)
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# POST /api/faculty/clubs/<id>/leave
# ---------------------------------------------------------------------------

def test_faculty_leave_club_success(client, faculty_headers):
    """Faculty coordinator can step down from AI Club."""
    response = client.post(
        f'/api/faculty/clubs/{AI_CLUB}/leave',
        headers=faculty_headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert 'message' in body


def test_faculty_leave_club_not_coordinator(client, faculty_headers):
    """If faculty is not a coordinator for a club they don't belong to, returns 404 or 403."""
    # Club 3 (Sports Club) is seeded with a different faculty coordinator
    response = client.post(
        '/api/faculty/clubs/3/leave',
        headers=faculty_headers,
    )
    assert response.status_code in {403, 404}


def test_faculty_leave_invalid_club(client, faculty_headers):
    """Non-existent club returns 404."""
    response = client.post(
        f'/api/faculty/clubs/{INVALID_CLUB}/leave',
        headers=faculty_headers,
    )
    assert response.status_code == 404


def test_faculty_leave_club_unauthenticated(client):
    """Unauthenticated access returns 401."""
    response = client.post(f'/api/faculty/clubs/{AI_CLUB}/leave')
    assert response.status_code == 401


def test_faculty_leave_club_student_blocked(client, student_headers):
    """Student cannot call faculty-leave endpoint."""
    response = client.post(
        f'/api/faculty/clubs/{AI_CLUB}/leave',
        headers=student_headers,
    )
    assert response.status_code == 403


def test_faculty_leave_club_gone_from_my_clubs(client, faculty_headers):
    """After leaving, club must no longer appear in /my-clubs."""
    leave_resp = client.post(
        f'/api/faculty/clubs/{AI_CLUB}/leave',
        headers=faculty_headers,
    )
    assert leave_resp.status_code == 200

    my_clubs_resp = client.get('/api/faculty/my-clubs', headers=faculty_headers)
    assert my_clubs_resp.status_code == 200
    club_ids = [c['id'] for c in my_clubs_resp.get_json()]
    assert AI_CLUB not in club_ids


# ---------------------------------------------------------------------------
# GET /api/faculty/general-events
# ---------------------------------------------------------------------------

def test_faculty_general_events_returns_list(client, faculty_headers):
    """Endpoint returns a list."""
    response = client.get('/api/faculty/general-events', headers=faculty_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_faculty_general_events_only_general_type(client, faculty_headers):
    """Every returned event must have organizerType == 'GENERAL'."""
    response = client.get('/api/faculty/general-events', headers=faculty_headers)
    assert response.status_code == 200
    events = response.get_json()
    for event in events:
        assert event.get('organizerType') == 'GENERAL'


def test_faculty_general_events_unauthenticated(client):
    """Unauthenticated access returns 401."""
    response = client.get('/api/faculty/general-events')
    assert response.status_code == 401


def test_faculty_general_events_student_blocked(client, student_headers):
    """Student must receive 403."""
    response = client.get('/api/faculty/general-events', headers=student_headers)
    assert response.status_code == 403
