import pytest
from datetime import datetime, timedelta
from app.models import db
from app.models.user import User
from app.models.events import Event, EventSession, EventRegistration, ParticipantRoundStatus
from app.models.club import Club, ClubFaculty

def get_auth_headers(client, email, password):
    res = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert res.status_code == 200, f"Login failed for {email}"
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_attendance_overview_summary_and_sessions(client):
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    evt = Event.query.first()

    res = client.get(f'/api/events/{evt.id}/attendance', headers=fac_headers)
    assert res.status_code == 200
    data = res.get_json()

    assert data['success'] is True
    assert 'sessions' in data
    assert len(data['sessions']) > 0
    assert 'presentCount' in data['sessions'][0]
    assert 'summary' in data
    assert 'total' in data['summary']

def test_session_creation_and_marking_flow(client):
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    evt = Event.query.first()

    # 1. Create a new session
    today_str = datetime.utcnow().date().isoformat()
    res_add = client.post(f'/api/events/{evt.id}/sessions', json={
        'name': 'Round 2 - Workspace Session',
        'sessionDate': today_str,
        'startTime': '10:00:00',
        'endTime': '12:00:00',
        'description': 'Workspace testing session'
    }, headers=fac_headers)
    assert res_add.status_code in (200, 201)

    # 2. Get attendance for the new session
    res_att = client.get(f'/api/events/{evt.id}/attendance', headers=fac_headers)
    assert res_att.status_code == 200
    new_sess = [s for s in res_att.get_json()['sessions'] if 'Workspace Session' in s['name']][0]

    student = User.query.filter_by(email='ananya@allclub.com').first()

    # 3. Save attendance in the new session
    res_save = client.post(f'/api/events/{evt.id}/attendance', json={
        'sessionId': new_sess['id'],
        'records': [{'userId': student.id, 'status': 'PRESENT'}]
    }, headers=fac_headers)
    assert res_save.status_code == 200

    # 4. Verify updated session summary count
    res_check = client.get(f'/api/events/{evt.id}/attendance?sessionId={new_sess["id"]}', headers=fac_headers)
    assert res_check.status_code == 200
    data_check = res_check.get_json()
    assert data_check['summary']['present'] >= 1
