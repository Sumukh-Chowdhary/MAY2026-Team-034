import pytest
from app.models import db
from app.models.user import User
from app.models.events import Event, EventSession, EventRegistration
from app.models.notification import Notification
from app.services.notification_service import NotificationService

def get_auth_headers(client, email, password):
    res = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert res.status_code == 200, f"Login failed for {email}"
    token = res.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_comprehensive_event_notifications(client):
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    student_headers = get_auth_headers(client, 'ananya@allclub.com', 'student123')

    student = User.query.filter_by(email='ananya@allclub.com').first()
    faculty = User.query.filter_by(email='meena@allclub.com').first()
    evt = Event.query.first()
    evt_id = evt.id

    # 1. Event Registration Notification
    EventRegistration.query.filter_by(event_id=evt_id, user_id=student.id).delete()
    db.session.commit()

    res_reg = client.post(f'/api/events/{evt_id}/register', headers=student_headers)
    assert res_reg.status_code in (200, 201)

    reg_notif = Notification.query.filter_by(user_id=student.id, type='EVENT_REGISTERED').first()
    assert reg_notif is not None
    assert "Registration Confirmed" in reg_notif.title
    assert reg_notif.entity_id == evt_id

    # 2. Schedule Change Notification
    NotificationService.notify_event_schedule_changed(evt_id, evt.event_name, "Rescheduled to 25 Aug", [student.id])
    sched_notif = Notification.query.filter_by(user_id=student.id, type='EVENT_SCHEDULE_CHANGED').first()
    assert sched_notif is not None
    assert "Schedule Updated" in sched_notif.title

    # 3. Venue Change Notification
    NotificationService.notify_event_venue_changed(evt_id, evt.event_name, "Main Auditorium", [student.id])
    venue_notif = Notification.query.filter_by(user_id=student.id, type='EVENT_VENUE_CHANGED').first()
    assert venue_notif is not None
    assert "Venue Updated" in venue_notif.title

    # 4. Event Announcement Notification
    res_ann = client.post(f'/api/events/{evt_id}/announcements', json={
        'title': 'Track Change',
        'message': 'Round 1 begins in Hall A'
    }, headers=fac_headers)
    assert res_ann.status_code == 200

    ann_notif = Notification.query.filter_by(user_id=student.id, type='ANNOUNCEMENT').first()
    assert ann_notif is not None
    assert "Track Change" in ann_notif.title

    # 5. Round Progression Notifications (Shortlisted, Eliminated, Finalist, Winner)
    NotificationService.notify_participant_shortlisted(evt_id, evt.event_name, student.id, "Round 1")
    short_notif = Notification.query.filter_by(user_id=student.id, type='EVENT_SHORTLISTED').first()
    assert short_notif is not None
    assert "Shortlisted" in short_notif.title

    NotificationService.notify_participant_eliminated(evt_id, evt.event_name, student.id, "Round 2", "Score cut-off")
    elim_notif = Notification.query.filter_by(user_id=student.id, type='EVENT_ELIMINATED').first()
    assert elim_notif is not None
    assert "eliminated" in elim_notif.message

    NotificationService.notify_participant_finalist(evt_id, evt.event_name, student.id)
    fin_notif = Notification.query.filter_by(user_id=student.id, type='EVENT_FINALIST').first()
    assert fin_notif is not None
    assert "Finalist" in fin_notif.title

    NotificationService.notify_participant_winner(evt_id, evt.event_name, student.id, "Winner")
    win_notif = Notification.query.filter_by(user_id=student.id, type='EVENT_WINNER').first()
    assert win_notif is not None
    assert "Congratulations" in win_notif.title

    # 6. Event Cancellation Notification
    NotificationService.notify_event_cancelled(evt_id, evt.event_name, [student.id])
    cancel_notif = Notification.query.filter_by(user_id=student.id, type='EVENT_CANCELLED').first()
    assert cancel_notif is not None
    assert "Cancelled" in cancel_notif.title

    # 7. Club Status Change Notification
    NotificationService.notify_club_status_changed(1, "Drama Club", "active", [student.id])
    club_notif = Notification.query.filter_by(user_id=student.id, type='CLUB_UPDATED').first()
    assert club_notif is not None
    assert "Club Active" in club_notif.title
