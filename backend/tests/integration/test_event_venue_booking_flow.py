import pytest

def test_event_venue_booking_and_registration_integration(client, admin_headers, student_headers, faculty_headers):
    # 1. Admin creates a new venue
    venue_response = client.post(
        '/api/venues/create',
        headers=admin_headers,
        json={
            'name': 'Integration Auditorium',
            'location': 'Block E, Floor 1',
            'type': 'AUDITORIUM',
            'capacity': 100
        }
    )
    assert venue_response.status_code == 201
    venue_id = venue_response.get_json()['id']

    # 2. Faculty creates a new event
    event_response = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': 1,
            'name': 'Integration Annual Meet',
            'description': 'End-to-end integration test event',
            'startDate': '2026-10-15',
            'endDate': '2026-10-15',
            'startTime': '10:00:00',
            'endTime': '16:00:00',
            'capacity': 80
        }
    )
    assert event_response.status_code == 201
    event_id = event_response.get_json()['id']

    # 3. Faculty assigns the newly created venue to the event
    assign_response = client.post(
        f'/api/events/{event_id}/venue',
        headers=faculty_headers,
        json={'venueId': venue_id}
    )
    assert assign_response.status_code == 200
    assert assign_response.get_json()['venueId'] == venue_id

    # 4. Student registers for the event
    register_response = client.post(
        f'/api/events/{event_id}/register',
        headers=student_headers
    )
    assert register_response.status_code in {200, 201}

    # 5. Faculty retrieves the registrations list to verify the student registration
    registrations_response = client.get(
        f'/api/events/{event_id}/registrations',
        headers=faculty_headers
    )
    assert registrations_response.status_code == 200
    registrations = registrations_response.get_json()
    
    # User ID 24 is Rahul (the student in the default test fixtures login)
    assert any(reg['userId'] == 24 for reg in registrations)
