# Sprint 2 – Venue Availability API tests
# Covers: GET /api/venues/<id>/availability  (no tests existed in Sprint 1)

VENUE_1 = 1   # Innovation Lab (seeded)
VENUE_2 = 2   # Main Auditorium (seeded)
INVALID_VENUE = 9999


# ---------------------------------------------------------------------------
# GET /api/venues/<id>/availability
# ---------------------------------------------------------------------------

def test_venue_availability_no_dates_returns_available(client, admin_headers):
    """Without date params, endpoint says venue is available."""
    response = client.get(f'/api/venues/{VENUE_1}/availability', headers=admin_headers)
    assert response.status_code == 200
    body = response.get_json()
    assert body['available'] is True
    assert body['conflictingEvent'] is None


def test_venue_availability_free_date_range(client, admin_headers):
    """A date range with no bookings must return available=True."""
    response = client.get(
        f'/api/venues/{VENUE_1}/availability?startDate=2030-01-01&endDate=2030-01-02',
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body['available'] is True
    assert body['conflictingEvent'] is None


def test_venue_availability_conflict_detected(client, admin_headers, faculty_headers):
    """Date range that overlaps an existing event must return available=False."""
    # First create an event that uses venue 2 on a specific date
    create_resp = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': 1,
            'name': 'Overlap Event',
            'startDate': '2027-06-01',
            'endDate': '2027-06-03',
            'venueId': VENUE_2,
        },
    )
    assert create_resp.status_code == 201

    # Check availability for overlapping range
    response = client.get(
        f'/api/venues/{VENUE_2}/availability?startDate=2027-06-02&endDate=2027-06-04',
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body['available'] is False
    assert body['conflictingEvent'] is not None
    assert body['conflictingEvent']['name'] == 'Overlap Event'


def test_venue_availability_adjacent_dates_not_conflict(client, admin_headers, faculty_headers):
    """Date range immediately after an event should NOT conflict."""
    # Create event occupying June 10-12
    client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': 1,
            'name': 'Adjacent Test Event',
            'startDate': '2027-06-10',
            'endDate': '2027-06-12',
            'venueId': VENUE_1,
        },
    )
    # Check June 13 onwards – should be clear
    response = client.get(
        f'/api/venues/{VENUE_1}/availability?startDate=2027-06-13&endDate=2027-06-15',
        headers=admin_headers,
    )
    assert response.status_code == 200
    # Adjacent dates should be available (not overlapping)
    body = response.get_json()
    assert body['available'] is True


def test_venue_availability_invalid_venue(client, admin_headers):
    """Non-existent venue returns 404."""
    response = client.get(
        f'/api/venues/{INVALID_VENUE}/availability',
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_venue_availability_unauthenticated(client):
    """Unauthenticated access returns 401."""
    response = client.get(f'/api/venues/{VENUE_1}/availability')
    assert response.status_code == 401


def test_venue_availability_cancelled_event_not_conflict(client, admin_headers, faculty_headers):
    """A CANCELLED event on the same dates must NOT block the venue."""
    # Create an event and then cancel it
    create_resp = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': 1,
            'name': 'Cancelled Event',
            'startDate': '2028-03-01',
            'endDate': '2028-03-02',
            'venueId': VENUE_1,
        },
    )
    assert create_resp.status_code == 201
    event_id = create_resp.get_json()['id']

    # Cancel the event
    cancel_resp = client.patch(
        f'/api/events/{event_id}/status',
        headers=admin_headers,
        json={'status': 'CANCELLED'},
    )
    assert cancel_resp.status_code == 200

    # Availability check should now say available
    avail_resp = client.get(
        f'/api/venues/{VENUE_1}/availability?startDate=2028-03-01&endDate=2028-03-02',
        headers=admin_headers,
    )
    assert avail_resp.status_code == 200
    assert avail_resp.get_json()['available'] is True


def test_venue_availability_student_can_check(client, student_headers):
    """Student (non-admin) can also check venue availability."""
    response = client.get(
        f'/api/venues/{VENUE_1}/availability?startDate=2031-01-01&endDate=2031-01-02',
        headers=student_headers,
    )
    assert response.status_code == 200
    assert response.get_json()['available'] is True
