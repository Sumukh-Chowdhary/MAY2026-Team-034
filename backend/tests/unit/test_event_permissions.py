import pytest
from app.models import db
from app.models.club import Club, ClubFaculty, ClubMembership
from app.models.events import Event
from app.models.tickets import Request

def get_auth_headers(client, username_or_email, password):
    res = client.post('/api/auth/login', json={'username': username_or_email, 'password': password})
    assert res.status_code == 200, f"Login failed for {username_or_email}"
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_club_member_volunteer_eligibility(client, app):
    sm_headers = get_auth_headers(client, 'Y24CS001', 'student123')
    
    with app.app_context():
        drama_evt = Event.query.filter_by(club_id=1).first() or Event.query.first()
        evt_id = drama_evt.id
        evt_name = drama_evt.event_name

    # 1. Member attempt to apply as volunteer -> 201 Created or 409 Pending
    res = client.post('/api/requests', json={
        'title': 'Volunteer Application for Drama',
        'requestType': 'BECOME_VOLUNTEER',
        'referenceType': 'EVENT',
        'referenceId': evt_id,
        'referenceName': evt_name
    }, headers=sm_headers)
    assert res.status_code in (201, 409)

def test_attendance_sessions_and_permissions(client, app):
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    fac_drama_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')

    with app.app_context():
        from app.models.events import EventRegistration
        from datetime import datetime
        drama_evt = Event.query.filter_by(club_id=1).first() or Event.query.first()
        evt_id = drama_evt.id
        today_d = datetime.utcnow().date()
        drama_evt.start_date = today_d
        drama_evt.end_date = today_d
        for s in drama_evt.sessions:
            s.session_date = today_d
        if not EventRegistration.query.filter_by(event_id=evt_id, user_id=24).first():
            db.session.add(EventRegistration(event_id=evt_id, user_id=24, registration_status='CONFIRMED'))
        db.session.commit()

    # 1. GET sessions for Drama event as Drama faculty -> 200 OK
    res_s = client.get(f'/api/events/{evt_id}/sessions', headers=fac_drama_headers)
    assert res_s.status_code == 200
    sessions = res_s.get_json()['data']
    assert len(sessions) >= 1
    session_id = sessions[0]['id']

    # 2. Drama Club Faculty CAN save attendance -> 200 OK
    res1 = client.post(f'/api/events/{evt_id}/attendance', json={
        'sessionId': session_id,
        'records': [{'userId': 24, 'status': 'PRESENT'}]
    }, headers=fac_drama_headers)
    assert res1.status_code == 200

    unauthorized_student_headers = get_auth_headers(client, 'Y25CS002', 'student123')

    # 3. Student non-organizer / non-volunteer CANNOT manage attendance -> 403 Forbidden
    res3 = client.post(f'/api/events/{evt_id}/attendance', json={
        'sessionId': session_id,
        'records': [{'userId': 24, 'status': 'PRESENT'}]
    }, headers=unauthorized_student_headers)
    assert res3.status_code == 403

    # 4. Admin CAN manage attendance for any event -> 200 OK
    res4 = client.post(f'/api/events/{evt_id}/attendance', json={
        'sessionId': session_id,
        'records': [{'userId': 24, 'status': 'PRESENT'}]
    }, headers=admin_headers)
    assert res4.status_code == 200
