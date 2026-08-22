# Sprint 2 – Event API tests
# Covers endpoints that had NO tests in Sprint 1:
#   GET  /api/events/calendar
#   GET  /api/events/organizer/my-events
#   POST /api/events/<id>/tickets

EVENT_ID = 1
CLUB_ID  = 1

# ---------------------------------------------------------------------------
# GET /api/events/calendar
# ---------------------------------------------------------------------------

def test_calendar_events_authenticated(client, student_headers):
    """Calendar returns a list for an authenticated user."""
    response = client.get('/api/events/calendar', headers=student_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_calendar_events_admin(client, admin_headers):
    """Admin can also retrieve calendar events."""
    response = client.get('/api/events/calendar', headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_calendar_events_faculty(client, faculty_headers):
    """Faculty can retrieve calendar events."""
    response = client.get('/api/events/calendar', headers=faculty_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_calendar_events_unauthenticated(client):
    """Unauthenticated request to calendar must be rejected."""
    response = client.get('/api/events/calendar')
    assert response.status_code == 401


def test_calendar_events_structure(client, admin_headers):
    """Each calendar item should have at minimum an id and name field."""
    response = client.get('/api/events/calendar', headers=admin_headers)
    assert response.status_code == 200
    items = response.get_json()
    if items:
        first = items[0]
        assert 'id' in first
        assert 'name' in first


# ---------------------------------------------------------------------------
# GET /api/events/organizer/my-events
# ---------------------------------------------------------------------------

def test_organizer_my_events_returns_list(client, admin_headers):
    """Endpoint returns a list (may be empty if no organizer assignments)."""
    response = client.get('/api/events/organizer/my-events', headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_organizer_my_events_student(client, student_headers):
    """Student who is an event organizer gets their events back."""
    # Rahul is seeded as organizer for AI Hack Sprint via EventOrganizer
    response = client.get('/api/events/organizer/my-events', headers=student_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_organizer_my_events_unauthenticated(client):
    """Unauthenticated access must return 401."""
    response = client.get('/api/events/organizer/my-events')
    assert response.status_code == 401


def test_organizer_my_events_faculty(client, faculty_headers):
    """Faculty user can call the endpoint without error."""
    response = client.get('/api/events/organizer/my-events', headers=faculty_headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_organizer_my_events_after_assigning(client, admin_headers, student_headers):
    """After assigning student as organizer, their managed events list grows."""
    # Assign student (Rahul, id=24) as organizer to event 1
    assign_resp = client.post(
        f'/api/events/{EVENT_ID}/organizers',
        headers=admin_headers,
        json={'userId': 24, 'role': 'ORGANIZER'},
    )
    assert assign_resp.status_code == 200

    # Now Rahul's managed events should include EVENT_ID
    my_events_resp = client.get(
        '/api/events/organizer/my-events',
        headers=student_headers,
    )
    assert my_events_resp.status_code == 200
    ids = [e['id'] for e in my_events_resp.get_json()]
    assert EVENT_ID in ids


# ---------------------------------------------------------------------------
# POST /api/events/<id>/tickets  (student raises an event ticket)
# ---------------------------------------------------------------------------

def test_create_event_ticket_success(client, student_headers):
    """Student can raise a ticket for an event."""
    response = client.post(
        f'/api/events/{EVENT_ID}/tickets',
        headers=student_headers,
        json={
            'title': 'Need more info on registration',
            'description': 'Can you clarify the team size limit?',
            'targetRole': 'ORGANIZER',
            'priority': 'MEDIUM',
        },
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body['success'] is True
    assert 'data' in body


def test_create_event_ticket_title_required(client, student_headers):
    """Ticket creation without title must return 400."""
    response = client.post(
        f'/api/events/{EVENT_ID}/tickets',
        headers=student_headers,
        json={'description': 'No title provided', 'targetRole': 'ORGANIZER'},
    )
    assert response.status_code == 400


def test_create_event_ticket_invalid_event(client, student_headers):
    """Creating a ticket for a non-existent event returns 404."""
    response = client.post(
        '/api/events/9999/tickets',
        headers=student_headers,
        json={'title': 'Ghost event ticket'},
    )
    assert response.status_code == 404


def test_create_event_ticket_coordinator_target(client, student_headers):
    """Student can target COORDINATOR (faculty) for the ticket."""
    response = client.post(
        f'/api/events/{EVENT_ID}/tickets',
        headers=student_headers,
        json={
            'title': 'Faculty approval needed',
            'description': 'Please confirm attendance policy.',
            'targetRole': 'COORDINATOR',
            'priority': 'HIGH',
        },
    )
    assert response.status_code == 201
    assert response.get_json()['success'] is True


def test_create_event_ticket_unauthenticated(client):
    """Unauthenticated ticket creation returns 401."""
    response = client.post(
        f'/api/events/{EVENT_ID}/tickets',
        json={'title': 'Anonymous ticket'},
    )
    assert response.status_code == 401


def test_create_event_ticket_admin(client, admin_headers):
    """Admin can also raise a ticket for an event."""
    response = client.post(
        f'/api/events/{EVENT_ID}/tickets',
        headers=admin_headers,
        json={'title': 'Admin-raised ticket', 'targetRole': 'ORGANIZER'},
    )
    assert response.status_code == 201
