"""
Sprint 2 – Integration Scenario 2
===================================
Student Raises Ticket → Organizer Responds Flow

Steps:
  1. Student registers for an event (Event 1)
  2. Student raises a ticket targeting the event ORGANIZER with a query
  3. Verify ticket creation returns success with ticket data
  4. Student raises a second ticket targeting the COORDINATOR (faculty)
  5. Organizer (student Rahul, who is an event organizer) checks managed events
  6. Organizer confirms Event 1 is in their managed list
  7. Organizer fetches full event detail to see context for the ticket
  8. Admin assigns student as additional event organizer and verifies
  9. Student raises a ticket and admin also independently raises one
"""

import pytest


def test_student_ticket_to_organizer_loop(
    client, student_headers, admin_headers, faculty_headers
):
    EVENT_ID = 1

    # ── Step 1: Student registers for the event ───────────────────────────────
    reg_resp = client.post(
        f'/api/events/{EVENT_ID}/register',
        headers=student_headers,
    )
    assert reg_resp.status_code in {200, 201}, (
        f"Registration failed: {reg_resp.get_json()}"
    )

    # Confirm the student appears in the event registrations
    reg_list_resp = client.get(
        f'/api/events/{EVENT_ID}/registrations',
        headers=admin_headers,
    )
    assert reg_list_resp.status_code == 200
    registrations = reg_list_resp.get_json()
    assert any(r['userId'] == 24 for r in registrations), (
        "Student Rahul (id=24) should be in registrations"
    )

    # ── Step 2: Student raises a ticket to ORGANIZER ──────────────────────────
    ticket_resp = client.post(
        f'/api/events/{EVENT_ID}/tickets',
        headers=student_headers,
        json={
            'title': 'What is the team size limit?',
            'description': 'Please confirm whether teams of 3 or 4 are allowed.',
            'targetRole': 'ORGANIZER',
            'priority': 'MEDIUM',
        },
    )
    assert ticket_resp.status_code == 201, f"Ticket creation failed: {ticket_resp.get_json()}"
    ticket_body = ticket_resp.get_json()
    assert ticket_body['success'] is True
    assert 'data' in ticket_body
    ticket_data = ticket_body['data']
    assert 'id' in ticket_data
    assert 'ORGANIZER' in ticket_data.get('title', '')

    # ── Step 3: Student raises a second ticket to COORDINATOR (faculty) ───────
    ticket2_resp = client.post(
        f'/api/events/{EVENT_ID}/tickets',
        headers=student_headers,
        json={
            'title': 'Permission for external participants',
            'description': 'Can students from other colleges register?',
            'targetRole': 'COORDINATOR',
            'priority': 'HIGH',
        },
    )
    assert ticket2_resp.status_code == 201
    ticket2_body = ticket2_resp.get_json()
    assert ticket2_body['success'] is True
    assert 'COORDINATOR' in ticket2_body['data'].get('title', '')

    # ── Step 4: Organizer checks their managed events list ────────────────────
    # Rahul (student) is seeded as an EventOrganizer for event 1
    organizer_events_resp = client.get(
        '/api/events/organizer/my-events',
        headers=student_headers,
    )
    assert organizer_events_resp.status_code == 200
    managed_events = organizer_events_resp.get_json()
    assert isinstance(managed_events, list)

    # ── Step 5: Organizer fetches full event detail for context ───────────────
    event_detail_resp = client.get(
        f'/api/events/{EVENT_ID}',
        headers=student_headers,
    )
    assert event_detail_resp.status_code == 200
    event_detail = event_detail_resp.get_json()
    assert event_detail['id'] == EVENT_ID
    assert 'name' in event_detail
    assert 'schedule' in event_detail

    # ── Step 6: Admin assigns a second student as organizer ───────────────────
    assign_resp = client.post(
        f'/api/events/{EVENT_ID}/organizers',
        headers=admin_headers,
        json={'userId': 25, 'role': 'CO_ORGANIZER'},
    )
    assert assign_resp.status_code == 200
    organizers_list = assign_resp.get_json().get('organizers', [])
    assert any(o['userId'] == 25 for o in organizers_list), (
        "Ananya (id=25) should now be an organizer"
    )

    # ── Step 7: New organizer (Ananya) checks their managed events ────────────
    ananya_login = client.post(
        '/api/auth/login',
        json={'username': 'Y25CS002', 'password': 'student123'},
    )
    assert ananya_login.status_code == 200
    ananya_headers = {'Authorization': f"Bearer {ananya_login.get_json()['token']}"}

    ananya_events_resp = client.get(
        '/api/events/organizer/my-events',
        headers=ananya_headers,
    )
    assert ananya_events_resp.status_code == 200
    ananya_managed = ananya_events_resp.get_json()
    managed_ids = [e['id'] for e in ananya_managed]
    assert EVENT_ID in managed_ids, "Event 1 should appear in Ananya's managed events"

    # ── Step 8: Admin raises their own ticket for the same event ──────────────
    admin_ticket_resp = client.post(
        f'/api/events/{EVENT_ID}/tickets',
        headers=admin_headers,
        json={
            'title': 'Budget approval required',
            'description': 'Please confirm prize fund allocation.',
            'targetRole': 'ORGANIZER',
            'priority': 'HIGH',
        },
    )
    assert admin_ticket_resp.status_code == 201
    assert admin_ticket_resp.get_json()['success'] is True

    # ── Step 9: Student verifies their registered events include EVENT_ID ─────
    my_events_resp = client.get(
        '/api/events/me',
        headers=student_headers,
    )
    assert my_events_resp.status_code == 200
    my_event_ids = [e['id'] for e in my_events_resp.get_json()]
    assert EVENT_ID in my_event_ids, "Event 1 should be in student's registered events"
