import pytest
from app.models import db
from app.models.user import User
from app.models.events import Event, EventSession, EventRegistration
from app.models.notification import Notification
from app.services.notification_service import NotificationService

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

def test_comprehensive_event_notifications(client, app):
    admin_headers = get_auth_headers(client, 'admin@allclub.com', 'admin123')
    fac_headers = get_auth_headers(client, 'meena@allclub.com', 'faculty123')
    student_headers = get_auth_headers(client, 'ananya@allclub.com', 'student123')

    with app.app_context():
        student = User.query.get(25)
        evt = Event.query.filter_by(club_id=1).first() or Event.query.first()
        evt_id = evt.id
        evt_name = evt.event_name
        student_id = student.id

        # 1. Event Registration Notification
        EventRegistration.query.filter_by(event_id=evt_id, user_id=student_id).delete()
        Notification.query.filter_by(user_id=student_id).delete()
        db.session.commit()

    res_reg = client.post(f'/api/events/{evt_id}/register', headers=student_headers)
    assert res_reg.status_code in (200, 201)

    with app.app_context():
        reg_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_REGISTERED').first()
        assert reg_notif is not None
        assert "Registration Confirmed" in reg_notif.title
        assert reg_notif.entity_id == evt_id

        # 2. Schedule Change Notification
        NotificationService.notify_event_schedule_changed(evt_id, evt_name, "Rescheduled to 25 Aug", [student_id])
        sched_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_SCHEDULE_CHANGED').first()
        assert sched_notif is not None
        assert "Schedule Updated" in sched_notif.title

        # 3. Venue Change Notification
        NotificationService.notify_event_venue_changed(evt_id, evt_name, "Main Auditorium", [student_id])
        venue_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_VENUE_CHANGED').first()
        assert venue_notif is not None
        assert "Venue Updated" in venue_notif.title

    # 4. Event Announcement Notification
    res_ann = client.post(f'/api/events/{evt_id}/announcements', json={
        'title': 'Track Change',
        'message': 'Round 1 begins in Hall A'
    }, headers=fac_headers)
    assert res_ann.status_code == 200

    with app.app_context():
        ann_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_ANNOUNCEMENT').first()
        if not ann_notif:
            ann_notif = Notification.query.filter_by(user_id=student_id).filter(Notification.title.like("%Track Change%")).first()
        assert ann_notif is not None

        # 5. Round Progression Notifications (Shortlisted, Eliminated, Finalist, Winner)
        NotificationService.notify_participant_shortlisted(evt_id, evt_name, student_id, "Round 1")
        short_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_SHORTLISTED').first()
        assert short_notif is not None
        assert "Shortlisted" in short_notif.title

        NotificationService.notify_participant_eliminated(evt_id, evt_name, student_id, "Round 2", "Score cut-off")
        elim_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_ELIMINATED').first()
        assert elim_notif is not None
        assert "eliminated" in elim_notif.message

        NotificationService.notify_participant_finalist(evt_id, evt_name, student_id)
        fin_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_FINALIST').first()
        assert fin_notif is not None
        assert "Finalist" in fin_notif.title

        NotificationService.notify_participant_winner(evt_id, evt_name, student_id, "Winner")
        win_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_WINNER').first()
        assert win_notif is not None

        # 6. Event Cancellation Notification
        NotificationService.notify_event_cancelled(evt_id, evt_name, [student_id])
        cancel_notif = Notification.query.filter_by(user_id=student_id, type='EVENT_CANCELLED').first()
        assert cancel_notif is not None
        assert "Cancelled" in cancel_notif.title

        # 7. Club Status Change Notification
        NotificationService.notify_club_status_changed(1, "Drama Club", "active", [student_id])
        club_notif = Notification.query.filter_by(user_id=student_id, type='CLUB_UPDATED').first()
        assert club_notif is not None
        assert "Club Active" in club_notif.title
