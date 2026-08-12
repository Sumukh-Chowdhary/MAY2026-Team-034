import pytest
from datetime import datetime, timedelta
from app.models import db
from app.models.user import User
from app.models.events import Event, EventSession, EventRegistration
from app.models.club import Club, ClubFaculty, ClubOrganizer

def get_auth_headers(client, email, password):
    res = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert res.status_code == 200, f"Login failed for {email}"
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_future_event_attendance_rejected(client):
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    faculty = User.query.filter_by(email='meena@allclub.com').first()

    today = datetime.utcnow().date()
    future_date = today + timedelta(days=10)

    club = Club.query.first()
    future_evt = Event(
        club_id=club.id,
        created_by=faculty.id,
        event_name="Future AI Summit 2030",
        event_description="Upcoming event",
        start_date=future_date,
        end_date=future_date,
        event_status="SCHEDULED"
    )
    db.session.add(future_evt)
    db.session.commit()

    student = User.query.filter_by(email='ananya@allclub.com').first()
    reg = EventRegistration(event_id=future_evt.id, user_id=student.id)
    db.session.add(reg)
    db.session.commit()

    # Faculty attempt to take attendance for future event -> Must be rejected (400)
    res_fac = client.post(f'/api/events/{future_evt.id}/attendance', json={
        'records': [{'userId': student.id, 'status': 'PRESENT'}]
    }, headers=fac_headers)

    assert res_fac.status_code == 400
    assert 'Attendance unavailable' in res_fac.get_json()['error']

    # Admin attempt -> Should be allowed (admin override for prep)
    res_admin = client.post(f'/api/events/{future_evt.id}/attendance', json={
        'records': [{'userId': student.id, 'status': 'PRESENT'}]
    }, headers=admin_headers)
    assert res_admin.status_code == 200

def test_current_or_past_event_attendance_allowed(client):
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    faculty = User.query.filter_by(email='meena@allclub.com').first()
    evt = Event.query.first()
    evt.created_by = faculty.id

    student = User.query.filter_by(email='ananya@allclub.com').first()

    # Ensure event start_date is today or past
    evt.start_date = datetime.utcnow().date() - timedelta(days=1)
    db.session.commit()

    res = client.post(f'/api/events/{evt.id}/attendance', json={
        'records': [{'userId': student.id, 'status': 'PRESENT'}]
    }, headers=fac_headers)

    assert res.status_code == 200
    assert res.get_json()['success'] is True

def test_unauthorized_faculty_attendance_rejected(client):
    # Faculty 'meena@allclub.com' is not coordinator/creator for this new club event
    meena_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    admin = User.query.filter_by(email='admin@allclub.com').first()

    # Create club with no meena assignment
    other_club = Club(club_name="Other Unaffiliated Club", club_category="CULTURAL", club_description="Test club description", club_status="ACTIVE")
    db.session.add(other_club)
    db.session.commit()

    unauth_evt = Event(
        club_id=other_club.id,
        created_by=admin.id,
        event_name="Other Club Event",
        start_date=datetime.utcnow().date(),
        end_date=datetime.utcnow().date(),
        event_status="LIVE"
    )
    db.session.add(unauth_evt)
    db.session.commit()

    res = client.post(f'/api/events/{unauth_evt.id}/attendance', json={
        'records': [{'userId': 1, 'status': 'PRESENT'}]
    }, headers=meena_headers)

    assert res.status_code == 403
    assert 'do not have permission' in res.get_json()['error']
