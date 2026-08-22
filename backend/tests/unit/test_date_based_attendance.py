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

def test_future_event_attendance_rejected(client, app):
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    
    today = datetime.utcnow().date()
    future_date = today + timedelta(days=10)

    with app.app_context():
        faculty = User.query.filter_by(email='meena@allclub.com').first()
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
        db.session.flush()

        student = User.query.get(25)
        reg = EventRegistration(event_id=future_evt.id, user_id=student.id)
        db.session.add(reg)
        db.session.commit()
        evt_id = future_evt.id
        student_id = student.id

    # Faculty attempt to take attendance for future event -> Must be rejected (400)
    res_fac = client.post(f'/api/events/{evt_id}/attendance', json={
        'records': [{'userId': student_id, 'status': 'PRESENT'}]
    }, headers=fac_headers)

    assert res_fac.status_code == 400
    assert 'Attendance unavailable' in res_fac.get_json()['error']

    # Admin attempt -> Should be allowed (admin override for prep)
    res_admin = client.post(f'/api/events/{evt_id}/attendance', json={
        'records': [{'userId': student_id, 'status': 'PRESENT'}]
    }, headers=admin_headers)
    assert res_admin.status_code == 200

def test_current_or_past_event_attendance_allowed(client, app):
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    with app.app_context():
        faculty = User.query.filter_by(email='meena@allclub.com').first()
        evt = Event.query.filter_by(club_id=1).first() or Event.query.first()
        evt.created_by = faculty.id
        past_d = datetime.utcnow().date() - timedelta(days=1)
        evt.start_date = past_d
        evt.end_date = past_d
        for s in evt.sessions:
            s.session_date = past_d
        student = User.query.get(25)
        
        # Ensure student is registered for event
        existing_reg = EventRegistration.query.filter_by(event_id=evt.id, user_id=student.id).first()
        if not existing_reg:
            db.session.add(EventRegistration(event_id=evt.id, user_id=student.id))
        db.session.commit()
        evt_id = evt.id
        student_id = student.id

    res = client.post(f'/api/events/{evt_id}/attendance', json={
        'records': [{'userId': student_id, 'status': 'PRESENT'}]
    }, headers=fac_headers)

    assert res.status_code == 200
    assert res.get_json()['success'] is True

def test_unauthorized_faculty_attendance_rejected(client, app):
    # Faculty 'meena@allclub.com' is not coordinator/creator for this new club event
    meena_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    
    with app.app_context():
        admin = User.query.filter_by(email='admin@allclub.com').first()

        # Create club with no meena assignment
        other_club = Club(club_name="Other Unaffiliated Club", club_category="CULTURAL", club_description="Test club description", club_status="ACTIVE")
        db.session.add(other_club)
        db.session.flush()

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
        evt_id = unauth_evt.id

    res = client.post(f'/api/events/{evt_id}/attendance', json={
        'records': [{'userId': 1, 'status': 'PRESENT'}]
    }, headers=meena_headers)

    assert res.status_code == 403
    assert 'do not have permission' in res.get_json()['error']
