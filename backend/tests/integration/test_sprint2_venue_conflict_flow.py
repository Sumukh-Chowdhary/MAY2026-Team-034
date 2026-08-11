"""
Sprint 2 – Integration Scenario 1
===================================
Venue Conflict & Re-booking Flow

Steps:
  1. Faculty A creates Event X and assigns Venue 1 to it (Jun 1–5 2027)
  2. Faculty B checks Venue 1 for the same dates → conflict detected
  3. Faculty B checks Venue 2 for the same dates → no conflict
  4. Faculty B creates Event Y on Venue 2 with the same dates → succeeds
  5. Verify both events coexist with different venues in the events list
  6. Admin cancels Event X → Venue 1 becomes available again
  7. Confirm Venue 1 is now free for those dates
"""

import pytest


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def faculty_b_headers(client):
    """Log in as Dr. Arjun Nair (second faculty in seed data)."""
    resp = client.post(
        '/api/auth/login',
        json={'email': 'arjun@allclub.com', 'password': 'faculty123'},
    )
    assert resp.status_code == 200
    return {'Authorization': f"Bearer {resp.get_json()['token']}"}


# ──────────────────────────────────────────────────────────────────────────────
# Integration test
# ──────────────────────────────────────────────────────────────────────────────

def test_venue_conflict_and_rebooking_flow(
    client, faculty_headers, faculty_b_headers, admin_headers
):
    # ── Step 1: Faculty A creates Event X and books Venue 1 (Jun 1–5 2027) ──
    event_x_resp = client.post(
        '/api/events/create',
        headers=faculty_headers,
        json={
            'clubId': 1,
            'name': 'Event X – AI Summit',
            'description': 'Annual AI summit hosted by AI Club.',
            'startDate': '2027-06-01',
            'endDate': '2027-06-05',
            'venueId': 1,
        },
    )
    assert event_x_resp.status_code == 201, f"Event X creation failed: {event_x_resp.get_json()}"
    event_x_id = event_x_resp.get_json()['id']
    assert event_x_resp.get_json()['venueId'] == 1

    # ── Step 2: Faculty B checks Venue 1 for overlapping dates ──────────────
    conflict_check = client.get(
        '/api/venues/1/availability?startDate=2027-06-03&endDate=2027-06-06',
        headers=faculty_b_headers,
    )
    assert conflict_check.status_code == 200
    conflict_body = conflict_check.get_json()
    assert conflict_body['available'] is False, "Expected conflict on Venue 1"
    assert conflict_body['conflictingEvent'] is not None
    assert conflict_body['conflictingEvent']['name'] == 'Event X – AI Summit'

    # ── Step 3: Faculty B checks Venue 2 — should be free ───────────────────
    venue2_check = client.get(
        '/api/venues/2/availability?startDate=2027-06-03&endDate=2027-06-06',
        headers=faculty_b_headers,
    )
    assert venue2_check.status_code == 200
    assert venue2_check.get_json()['available'] is True, "Venue 2 should be free"

    # ── Step 4: Faculty B creates Event Y on Venue 2 (same dates) ───────────
    event_y_resp = client.post(
        '/api/events/create',
        headers=faculty_b_headers,
        json={
            'clubId': 2,
            'name': 'Event Y – Robotics Expo',
            'description': 'Robotics club expo on the same dates.',
            'startDate': '2027-06-03',
            'endDate': '2027-06-06',
            'venueId': 2,
        },
    )
    assert event_y_resp.status_code == 201, f"Event Y creation failed: {event_y_resp.get_json()}"
    event_y_id = event_y_resp.get_json()['id']
    assert event_y_resp.get_json()['venueId'] == 2

    # ── Step 5: Both events coexist in the events list ───────────────────────
    all_events_resp = client.get('/api/events', headers=admin_headers)
    assert all_events_resp.status_code == 200
    all_events = all_events_resp.get_json()
    event_ids = [e['id'] for e in all_events]
    assert event_x_id in event_ids, "Event X missing from events list"
    assert event_y_id in event_ids, "Event Y missing from events list"

    # Confirm they have different venue IDs
    ex = next(e for e in all_events if e['id'] == event_x_id)
    ey = next(e for e in all_events if e['id'] == event_y_id)
    assert ex['venueId'] != ey['venueId'], "Both events should be in different venues"

    # ── Step 6: Admin cancels Event X ────────────────────────────────────────
    cancel_resp = client.patch(
        f'/api/events/{event_x_id}/status',
        headers=admin_headers,
        json={'status': 'CANCELLED'},
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.get_json()['status'] == 'CANCELLED'

    # ── Step 7: Venue 1 is now free for those dates ───────────────────────────
    freed_check = client.get(
        '/api/venues/1/availability?startDate=2027-06-01&endDate=2027-06-05',
        headers=faculty_b_headers,
    )
    assert freed_check.status_code == 200
    freed_body = freed_check.get_json()
    assert freed_body['available'] is True, (
        "Venue 1 should be free after Event X was cancelled"
    )
    assert freed_body['conflictingEvent'] is None
