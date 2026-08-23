import pytest
from app.models import db
from app.models.user import User, Role
from app.models.events import Event, EventSession, EventRegistration, EventAttendance, ParticipantRoundStatus, EventPrize, EventAnnouncement
from app.models.notification import Notification

def get_auth_headers(client, email_or_reg, password):
    payload = {'password': password}
    if '@' in email_or_reg:
        if 'student' in email_or_reg or email_or_reg.startswith('ananya') or email_or_reg.startswith('rahul'):
            payload['username'] = 'Y25CS002' if 'ananya' in email_or_reg else 'Y24CS001'
        else:
            payload['email'] = email_or_reg
    else:
        payload['username'] = email_or_reg
    res = client.post('/api/auth/login', json=payload)
    assert res.status_code == 200, f"Login failed for {email_or_reg}"
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_complete_competition_lifecycle_and_results(client, app):
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    student_headers = get_auth_headers(client, 'ananya@allclub.com', 'student123')

    # Get event
    with app.app_context():
        from datetime import datetime
        evt = Event.query.filter_by(club_id=1).first() or Event.query.first()
        evt_id = evt.id
        today_d = datetime.utcnow().date()
        evt.start_date = today_d
        evt.end_date = today_d
        EventSession.query.filter_by(event_id=evt_id).delete()
        for uid in [24, 25, 26]:
            if not EventRegistration.query.filter_by(event_id=evt_id, user_id=uid).first():
                db.session.add(EventRegistration(event_id=evt_id, user_id=uid, registration_status='CONFIRMED'))
        db.session.commit()

    # 1. Create 3 Rounds (Round 1, Round 2, Final)
    today_iso = datetime.utcnow().date().isoformat()
    res_r1 = client.post(f'/api/events/{evt_id}/sessions', json={
        'name': 'Round 1 — Preliminary',
        'roundNumber': 1,
        'sessionDate': today_iso,
        'status': 'ACTIVE'
    }, headers=fac_headers)
    assert res_r1.status_code == 201
    r1_id = res_r1.get_json()['data']['id']

    res_r2 = client.post(f'/api/events/{evt_id}/sessions', json={
        'name': 'Round 2 — Semi Final',
        'roundNumber': 2,
        'sessionDate': today_iso,
        'status': 'UPCOMING'
    }, headers=fac_headers)
    assert res_r2.status_code == 201
    r2_id = res_r2.get_json()['data']['id']

    res_r3 = client.post(f'/api/events/{evt_id}/sessions', json={
        'name': 'Round 3 — Final',
        'roundNumber': 3,
        'sessionDate': today_iso,
        'status': 'UPCOMING'
    }, headers=fac_headers)
    assert res_r3.status_code == 201
    r3_id = res_r3.get_json()['data']['id']

    # 2. Mark Round 1 Attendance for users 24, 25, 26
    client.post(f'/api/events/{evt_id}/attendance', json={
        'sessionId': r1_id,
        'records': [
            {'userId': 24, 'status': 'PRESENT'},
            {'userId': 25, 'status': 'PRESENT'},
            {'userId': 26, 'status': 'ABSENT'}
        ]
    }, headers=fac_headers)

    # Verify absent user 26 is NOT automatically eliminated
    with app.app_context():
        prs_26 = ParticipantRoundStatus.query.filter_by(session_id=r1_id, user_id=26).first()
        assert prs_26 is None or prs_26.status != 'ELIMINATED', "Absent user must NOT be automatically eliminated"

    # 3. Shortlist Users 24 and 25 from Round 1 to Round 2 (Eliminate user 26)
    client.post(f'/api/events/{evt_id}/sessions/{r1_id}/shortlist', json={
        'selectedUserIds': [24, 25],
        'reason': 'Scores below 70'
    }, headers=fac_headers)

    # 4. Check Round 2 Roster: ONLY 24 and 25 eligible, user 26 EXCLUDED
    res_r2_roster = client.get(f'/api/events/{evt_id}/attendance?sessionId={r2_id}', headers=fac_headers)
    r2_uids = [p['userId'] for p in res_r2_roster.get_json()['participants']]
    assert 24 in r2_uids and 25 in r2_uids
    assert 26 not in r2_uids, "Eliminated user 26 CANNOT appear in Round 2 roster"

    # 5. Shortlist Users 24 and 25 from Round 2 to Final (Eliminate user 26)
    client.post(f'/api/events/{evt_id}/sessions/{r2_id}/shortlist', json={
        'selectedUserIds': [24, 25],
        'reason': 'Semi final cut-off'
    }, headers=fac_headers)

    # 6. RESULT VALIDATION: Attempting to declare eliminated user 26 or non-finalist as Winner MUST FAIL (HTTP 400)
    res_invalid_win = client.post(f'/api/events/{evt_id}/results', json={
        'winnerUserId': 26
    }, headers=fac_headers)
    assert res_invalid_win.status_code == 400, "Declaring non-finalist user 26 as winner must be rejected"
    assert "did not reach the Final round" in res_invalid_win.get_json()['error']

    # 7. Declare Valid Winner (User 24 reached Final)
    res_valid_win = client.post(f'/api/events/{evt_id}/results', json={
        'winnerUserId': 24,
        'runnerUpUserId': 25
    }, headers=fac_headers)
    assert res_valid_win.status_code == 200, "Valid winner declaration must succeed"

    # 8. Announce Winners & Targeted Notifications
    res_ann_win = client.post(f'/api/events/{evt_id}/announce-winners', json={}, headers=fac_headers)
    assert res_ann_win.status_code == 200

    # Verify announcement created
    with app.app_context():
        ann = EventAnnouncement.query.filter_by(event_id=evt_id).order_by(EventAnnouncement.id.desc()).first()
        assert ann is not None
        assert "Results Announced" in ann.title

        # Verify targeted notifications generated
        notifs = Notification.query.filter_by(entity_id=evt_id, type='COMPETITION').all()
        assert len(notifs) > 0

    # 9. Test Unauthorized user results declaration (Returns 403)
    res_unauth = client.post(f'/api/events/{evt_id}/results', json={'winnerUserId': 24}, headers=student_headers)
    assert res_unauth.status_code == 403

    # 10. Admin Override
    res_admin_ann = client.post(f'/api/events/{evt_id}/announcements', json={
        'title': 'Grand Finale Completed',
        'message': 'Thank you all participants!'
    }, headers=admin_headers)
    assert res_admin_ann.status_code == 200
