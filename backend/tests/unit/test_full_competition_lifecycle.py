import pytest
from app.models import db
from app.models.user import User, Role
from app.models.events import Event, EventSession, EventRegistration, EventAttendance, ParticipantRoundStatus, EventPrize, EventAnnouncement
from app.models.notification import Notification

def get_auth_headers(client, email, password):
    res = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert res.status_code == 200, f"Login failed for {email}"
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_complete_competition_lifecycle_and_results(client):
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    student_headers = get_auth_headers(client, 'ananya@allclub.com', 'student123')

    # Get event
    evt = Event.query.filter_by(club_id=1).first() or Event.query.first()
    evt_id = evt.id

    # 1. Create 3 Rounds (Round 1, Round 2, Final)
    res_r1 = client.post(f'/api/events/{evt_id}/sessions', json={
        'name': 'Round 1 — Preliminary',
        'roundNumber': 1,
        'status': 'ACTIVE'
    }, headers=fac_headers)
    assert res_r1.status_code == 201
    r1_id = res_r1.get_json()['data']['id']

    res_r2 = client.post(f'/api/events/{evt_id}/sessions', json={
        'name': 'Round 2 — Semi Final',
        'roundNumber': 2,
        'status': 'UPCOMING'
    }, headers=fac_headers)
    assert res_r2.status_code == 201
    r2_id = res_r2.get_json()['data']['id']

    res_r3 = client.post(f'/api/events/{evt_id}/sessions', json={
        'name': 'Round 3 — Final',
        'roundNumber': 3,
        'status': 'UPCOMING'
    }, headers=fac_headers)
    assert res_r3.status_code == 201
    r3_id = res_r3.get_json()['data']['id']

    # 2. Mark Round 1 Attendance for users 6, 7, 8
    client.post(f'/api/events/{evt_id}/attendance', json={
        'sessionId': r1_id,
        'records': [
            {'userId': 6, 'status': 'PRESENT'},
            {'userId': 7, 'status': 'PRESENT'},
            {'userId': 8, 'status': 'ABSENT'}
        ]
    }, headers=fac_headers)

    # Verify absent user 8 is NOT automatically eliminated
    prs_8 = ParticipantRoundStatus.query.filter_by(session_id=r1_id, user_id=8).first()
    assert prs_8 is None or prs_8.status != 'ELIMINATED', "Absent user must NOT be automatically eliminated"

    # 3. Shortlist Users 6 and 7 from Round 1 to Round 2 (Eliminate user 8)
    client.post(f'/api/events/{evt_id}/sessions/{r1_id}/shortlist', json={
        'selectedUserIds': [6, 7],
        'reason': 'Scores below 70'
    }, headers=fac_headers)

    # 4. Check Round 2 Roster: ONLY 6 and 7 eligible, user 8 EXCLUDED
    res_r2_roster = client.get(f'/api/events/{evt_id}/attendance?sessionId={r2_id}', headers=fac_headers)
    r2_uids = [p['userId'] for p in res_r2_roster.get_json()['participants']]
    assert 6 in r2_uids and 7 in r2_uids
    assert 8 not in r2_uids, "Eliminated user 8 CANNOT appear in Round 2 roster"

    # 5. Shortlist Users 6 and 7 from Round 2 to Final (Eliminate user 8)
    client.post(f'/api/events/{evt_id}/sessions/{r2_id}/shortlist', json={
        'selectedUserIds': [6, 7],
        'reason': 'Semi final cut-off'
    }, headers=fac_headers)

    # 6. RESULT VALIDATION: Attempting to declare eliminated user 8 or 7 as Winner MUST FAIL (HTTP 400)
    res_invalid_win = client.post(f'/api/events/{evt_id}/results', json={
        'winnerUserId': 8
    }, headers=fac_headers)
    assert res_invalid_win.status_code == 400, "Declaring non-finalist user 8 as winner must be rejected"
    assert "did not reach the Final round" in res_invalid_win.get_json()['error']

    # 7. Declare Valid Winner (User 6 reached Final)
    res_valid_win = client.post(f'/api/events/{evt_id}/results', json={
        'winnerUserId': 6,
        'runnerUpUserId': 7
    }, headers=fac_headers)
    assert res_valid_win.status_code == 200, "Valid winner declaration must succeed"

    # 8. Announce Winners & Targeted Notifications
    res_ann_win = client.post(f'/api/events/{evt_id}/announce-winners', json={}, headers=fac_headers)
    assert res_ann_win.status_code == 200

    # Verify announcement created
    ann = EventAnnouncement.query.filter_by(event_id=evt_id).order_by(EventAnnouncement.id.desc()).first()
    assert ann is not None
    assert "Results Announced" in ann.title

    # Verify targeted notifications generated
    notifs = Notification.query.filter_by(entity_id=evt_id, type='COMPETITION').all()
    assert len(notifs) > 0

    # 9. Test Unauthorized user results declaration (Returns 403)
    res_unauth = client.post(f'/api/events/{evt_id}/results', json={'winnerUserId': 6}, headers=student_headers)
    assert res_unauth.status_code == 403

    # 10. Admin Override
    res_admin_ann = client.post(f'/api/events/{evt_id}/announcements', json={
        'title': 'Grand Finale Completed',
        'message': 'Thank you all participants!'
    }, headers=admin_headers)
    assert res_admin_ann.status_code == 200
