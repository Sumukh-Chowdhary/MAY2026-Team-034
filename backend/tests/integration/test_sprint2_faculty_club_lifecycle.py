"""
Sprint 2 – Integration Scenario 3
===================================
Faculty Club Lifecycle — Supervise, Update, Manage Members, Step Down

Steps:
  1. Faculty (Dr. Meena Rao) views her supervised clubs → AI Club present
  2. Faculty edits AI Club details (description, category)
  3. Faculty views club members list
  4. Faculty deactivates a member (Ananya, id=7)
  5. Faculty verifies member is now INACTIVE
  6. Faculty reactivates the member
  7. Faculty checks club events before stepping down
  8. Faculty steps down from AI Club coordinator role
  9. AI Club NO LONGER appears in faculty's my-clubs
  10. AI Club is still publicly accessible and ACTIVE (club unaffected)
"""

import pytest


def test_faculty_club_lifecycle_supervise_to_stepdown(
    client, faculty_headers, admin_headers, student_headers
):
    AI_CLUB = 1

    # ── Step 1: Faculty views supervised clubs ────────────────────────────────
    my_clubs_resp = client.get('/api/faculty/my-clubs', headers=faculty_headers)
    assert my_clubs_resp.status_code == 200
    my_clubs = my_clubs_resp.get_json()
    assert isinstance(my_clubs, list)
    assert len(my_clubs) > 0

    ai_club_entry = next((c for c in my_clubs if c['id'] == AI_CLUB), None)
    assert ai_club_entry is not None, "AI Club should be in faculty's supervised clubs"
    assert ai_club_entry['clubName'] == 'AI Club'
    assert ai_club_entry['status'] == 'ACTIVE'
    initial_member_count = ai_club_entry['memberCount']

    # ── Step 2: Faculty edits AI Club details ─────────────────────────────────
    # Note: facultyCoordinatorIds must include the current faculty's user_id (id=4 for Dr. Meena Rao)
    edit_resp = client.put(
        f'/api/faculty/clubs/{AI_CLUB}/edit',
        headers=faculty_headers,
        json={
            'name': 'AI Club',
            'description': 'Updated by faculty: Cutting-edge AI research club.',
            'category': 'Technology',
            'facultyCoordinatorIds': [4],  # Dr. Meena Rao's user_id = 4
        },
    )
    assert edit_resp.status_code == 200, f"Club edit failed: {edit_resp.get_json()}"
    edited_club = edit_resp.get_json()
    assert edited_club['description'] == 'Updated by faculty: Cutting-edge AI research club.'

    # ── Step 3: Faculty views all club members ────────────────────────────────
    members_resp = client.get(
        f'/api/faculty/clubs/{AI_CLUB}/members',
        headers=faculty_headers,
    )
    assert members_resp.status_code == 200
    members = members_resp.get_json()
    assert isinstance(members, list)
    assert len(members) > 0

    # Confirm Ananya (id=25) is an active member
    ananya_member = next((m for m in members if m['id'] == 25), None)
    assert ananya_member is not None, "Ananya (id=25) should be a club member"

    # ── Step 4: Faculty deactivates Ananya ───────────────────────────────────
    deactivate_resp = client.patch(
        f'/api/faculty/clubs/{AI_CLUB}/members/25/deactivate',
        headers=faculty_headers,
    )
    assert deactivate_resp.status_code == 200
    deactivated = deactivate_resp.get_json()
    assert deactivated['membershipStatus'] == 'INACTIVE'

    # ── Step 5: Verify member is INACTIVE in the members list ─────────────────
    members_after_resp = client.get(
        f'/api/faculty/clubs/{AI_CLUB}/members',
        headers=faculty_headers,
    )
    assert members_after_resp.status_code == 200
    members_after = members_after_resp.get_json()
    ananya_after = next((m for m in members_after if m['id'] == 25), None)
    assert ananya_after is not None
    assert ananya_after['membershipStatus'] == 'INACTIVE'

    # ── Step 6: Faculty reactivates Ananya ───────────────────────────────────
    reactivate_resp = client.patch(
        f'/api/faculty/clubs/{AI_CLUB}/members/25/reactivate',
        headers=faculty_headers,
    )
    assert reactivate_resp.status_code == 200
    assert reactivate_resp.get_json()['membershipStatus'] == 'ACTIVE'

    # ── Step 7: Faculty checks club events before stepping down ───────────────
    events_resp = client.get(
        f'/api/faculty/clubs/{AI_CLUB}/events',
        headers=faculty_headers,
    )
    assert events_resp.status_code == 200
    club_events = events_resp.get_json()
    assert isinstance(club_events, list)
    # AI Club has seeded events — should have at least one
    assert len(club_events) > 0, "AI Club should have at least one seeded event"
    event_names = [e['name'] for e in club_events]
    assert any('AI' in name or 'Hack' in name for name in event_names), (
        "AI Club events should include an AI-related event"
    )

    # ── Step 8: Faculty steps down from AI Club coordinator role ──────────────
    leave_resp = client.post(
        f'/api/faculty/clubs/{AI_CLUB}/leave',
        headers=faculty_headers,
    )
    assert leave_resp.status_code == 200
    leave_body = leave_resp.get_json()
    assert 'message' in leave_body

    # ── Step 9: AI Club no longer in faculty's my-clubs ───────────────────────
    my_clubs_after_resp = client.get('/api/faculty/my-clubs', headers=faculty_headers)
    assert my_clubs_after_resp.status_code == 200
    my_clubs_after = my_clubs_after_resp.get_json()
    remaining_ids = [c['id'] for c in my_clubs_after]
    assert AI_CLUB not in remaining_ids, (
        "AI Club should NOT appear in faculty's clubs after stepping down"
    )

    # ── Step 10: AI Club is still accessible and ACTIVE publicly ─────────────
    club_public_resp = client.get(
        f'/api/student/clubs/{AI_CLUB}',
        headers=student_headers,
    )
    assert club_public_resp.status_code == 200
    public_club = club_public_resp.get_json()
    assert public_club['id'] == AI_CLUB
    assert public_club['status'] == 'ACTIVE', (
        "AI Club should still be ACTIVE even after faculty stepped down"
    )
    assert public_club['name'] == 'AI Club'

    # Admin can also still see the club via admin endpoint
    admin_club_resp = client.get(
        f'/api/admin/clubs/{AI_CLUB}',
        headers=admin_headers,
    )
    assert admin_club_resp.status_code == 200
    assert admin_club_resp.get_json()['id'] == AI_CLUB
