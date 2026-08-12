import pytest
from app.models import db
from app.models.club import Club, ClubFaculty, ClubMembership
from app.models.events import Event
from app.models.tickets import Request

def get_auth_headers(client, email, password):
    res = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert res.status_code == 200, f"Login failed for {email}"
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_club_member_volunteer_eligibility(client):
    # Drama Club member: rahul@allclub.com
    # Non-member of Drama Club: vikram@allclub.com (or priya@allclub.com if not in Drama)
    sm_headers = get_auth_headers(client, 'rahul@allclub.com', 'student123')
    
    # Query Drama event
    drama_evt = Event.query.filter_by(club_id=1).first() # Drama Club
    if not drama_evt:
        drama_evt = Event.query.first()

    # 1. Member attempt to apply as volunteer -> 201 Created or 409 Pending
    res = client.post('/api/requests', json={
        'title': 'Volunteer Application for Drama',
        'requestType': 'BECOME_VOLUNTEER',
        'referenceType': 'EVENT',
        'referenceId': drama_evt.id,
        'referenceName': drama_evt.event_name
    }, headers=sm_headers)
    assert res.status_code in (201, 409)

def test_attendance_sessions_and_permissions(client):
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    fac_drama_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    student_headers = get_auth_headers(client, 'rahul@allclub.com', 'student123')

    drama_evt = Event.query.filter_by(club_id=1).first() or Event.query.first()

    # 1. GET sessions for Drama event as Drama faculty -> 200 OK
    res_s = client.get(f'/api/events/{drama_evt.id}/sessions', headers=fac_drama_headers)
    assert res_s.status_code == 200
    sessions = res_s.get_json()['data']
    assert len(sessions) >= 1
    session_id = sessions[0]['id']

    # 2. Drama Club Faculty CAN save attendance -> 200 OK
    res1 = client.post(f'/api/events/{drama_evt.id}/attendance', json={
        'sessionId': session_id,
        'records': [{'userId': 6, 'status': 'PRESENT'}]
    }, headers=fac_drama_headers)
    assert res1.status_code == 200

    unauthorized_student_headers = get_auth_headers(client, 'ananya@allclub.com', 'student123')

    # 3. Student non-organizer / non-volunteer CANNOT manage attendance -> 403 Forbidden
    res3 = client.post(f'/api/events/{drama_evt.id}/attendance', json={
        'sessionId': session_id,
        'records': [{'userId': 6, 'status': 'PRESENT'}]
    }, headers=unauthorized_student_headers)
    assert res3.status_code == 403

    # 4. Admin CAN manage attendance for any event -> 200 OK
    res4 = client.post(f'/api/events/{drama_evt.id}/attendance', json={
        'sessionId': session_id,
        'records': [{'userId': 6, 'status': 'PRESENT'}]
    }, headers=admin_headers)
    assert res4.status_code == 200
