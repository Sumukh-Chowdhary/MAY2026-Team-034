import pytest
from app.models import db
from app.models.user import User, Role
from app.models.club import Club, ClubFaculty
from app.models.events import Event, EventSession, EventRegistration, EventAttendance, ParticipantRoundStatus

def get_auth_headers(client, email_or_reg, password):
    payload = {'password': password}
    if '@' in email_or_reg:
        if 'student' in email_or_reg or email_or_reg.startswith('ananya') or email_or_reg.startswith('rahul'):
            # Student login uses registration ID
            payload['username'] = 'Y25CS002' if 'ananya' in email_or_reg else 'Y24CS001'
        else:
            payload['email'] = email_or_reg
    else:
        payload['username'] = email_or_reg
    res = client.post('/api/auth/login', json=payload)
    assert res.status_code == 200, f"Login failed for {email_or_reg}"
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_multi_round_competition_flow(client, app):
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    fac_drama_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    unauth_student_headers = get_auth_headers(client, 'ananya@allclub.com', 'student123')

    # Query Drama Event
    with app.app_context():
        from datetime import datetime
        drama_evt = Event.query.filter_by(club_id=1).first() or Event.query.first()
        evt_id = drama_evt.id
        today_d = datetime.utcnow().date()
        drama_evt.start_date = today_d
        drama_evt.end_date = today_d
        EventSession.query.filter_by(event_id=evt_id).delete()
        for uid in [24, 25]:
            if not EventRegistration.query.filter_by(event_id=evt_id, user_id=uid).first():
                db.session.add(EventRegistration(event_id=evt_id, user_id=uid, registration_status='CONFIRMED'))
        db.session.commit()

    # 1. Create Multiple Competition Rounds (Round 1, Round 2, Final)
    today_iso = datetime.utcnow().date().isoformat()
    res_r1 = client.post(f'/api/events/{evt_id}/sessions', json={
        'name': 'Round 1 — Preliminary',
        'roundNumber': 1,
        'sessionDate': today_iso,
        'status': 'ACTIVE',
        'startTime': '09:00 AM',
        'endTime': '11:00 AM'
    }, headers=fac_drama_headers)
    assert res_r1.status_code == 201
    r1_id = res_r1.get_json()['data']['id']

    res_r2 = client.post(f'/api/events/{evt_id}/sessions', json={
        'name': 'Round 2 — Semi Final',
        'roundNumber': 2,
        'sessionDate': today_iso,
        'status': 'UPCOMING',
        'startTime': '02:00 PM',
        'endTime': '04:00 PM'
    }, headers=fac_drama_headers)
    assert res_r2.status_code == 201
    r2_id = res_r2.get_json()['data']['id']

    # 2. Mark Round 1 Attendance for participants (e.g. users 24 and 25)
    res_att1 = client.post(f'/api/events/{evt_id}/attendance', json={
        'sessionId': r1_id,
        'records': [
            {'userId': 24, 'status': 'PRESENT'},
            {'userId': 25, 'status': 'PRESENT'}
        ]
    }, headers=fac_drama_headers)
    assert res_att1.status_code == 200

    # 3. Test Unauthorized Shortlisting Prevention (Returns 403)
    res_unauth = client.post(f'/api/events/{evt_id}/sessions/{r1_id}/shortlist', json={
        'selectedUserIds': [24],
        'reason': 'Not shortlisted'
    }, headers=unauth_student_headers)
    assert res_unauth.status_code == 403

    # 4. Authorized Shortlisting for Round 1 (Shortlist user 24, eliminate user 25)
    res_shortlist = client.post(f'/api/events/{evt_id}/sessions/{r1_id}/shortlist', json={
        'selectedUserIds': [24],
        'reason': 'Cut-off score not met'
    }, headers=fac_drama_headers)
    assert res_shortlist.status_code == 200

    # Verify status in database
    with app.app_context():
        prs_24 = ParticipantRoundStatus.query.filter_by(session_id=r1_id, user_id=24).first()
        prs_25 = ParticipantRoundStatus.query.filter_by(session_id=r1_id, user_id=25).first()
        assert prs_24 is not None and prs_24.status == 'SHORTLISTED'
        if prs_25:
            assert prs_25.status == 'ELIMINATED'
            assert prs_25.reason == 'Cut-off score not met'

    # 5. Round 2 Attendance ONLY loads Round 1 Shortlisted candidates (User 24 included, User 25 excluded)
    res_r2_att = client.get(f'/api/events/{evt_id}/attendance?sessionId={r2_id}', headers=fac_drama_headers)
    assert res_r2_att.status_code == 200
    r2_participants = res_r2_att.get_json()['participants']
    r2_uids = [p['userId'] for p in r2_participants]

    assert 24 in r2_uids, "Shortlisted candidate User 24 MUST be eligible for Round 2"
    assert 25 not in r2_uids, "Eliminated candidate User 25 MUST NOT appear in Round 2"

    # 6. Admin Override & Participant Progress View
    res_prog = client.get(f'/api/events/{evt_id}/participant-progress', headers=admin_headers)
    assert res_prog.status_code == 200
    progress_list = res_prog.get_json()['data']
    user24_prog = next((p for p in progress_list if p['userId'] == 24), None)
    assert user24_prog is not None
    assert len(user24_prog['roundsHistory']) >= 2
