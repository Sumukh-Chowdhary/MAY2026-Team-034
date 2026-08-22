import pytest

def test_volunteer_lifecycle_integration(client, app, student_headers, admin_headers):
    with app.app_context():
        from app.models.events import Event, EventVolunteer
        from app.models.user import User
        from app.routes.events import _can_manage_event
        from app.models import db

        user_24 = User.query.get(24)
        unauth_event = None
        for ev in Event.query.all():
            if not _can_manage_event(ev, user_24):
                unauth_event = ev
                break

        if not unauth_event:
            from datetime import datetime
            today_d = datetime.utcnow().date()
            ev = Event(event_name="Admin Exclusive Event", created_by=1, event_status="SCHEDULED", start_date=today_d, end_date=today_d)
            db.session.add(ev)
            db.session.commit()
            unauth_event = ev

        event_id = unauth_event.id
        EventVolunteer.query.filter_by(event_id=event_id, user_id=24).delete()
        db.session.commit()
    
    # 1. Student registers as a volunteer for the event
    register_resp = client.post(
        f"/api/events/{event_id}/volunteers",
        headers=student_headers,
        json={}
    )
    assert register_resp.status_code == 200
    volunteers = register_resp.get_json()["volunteers"]
    
    # User ID 24 is Rahul (logged in via student_headers)
    student_vol = next(item for item in volunteers if item["userId"] == 24)
    assert student_vol["status"] == "PENDING"
    volunteer_entry_id = student_vol["id"]
    
    # 2. Verify that a normal student cannot approve their own volunteer status
    forbidden_resp = client.patch(
        f"/api/events/{event_id}/volunteers/{volunteer_entry_id}",
        headers=student_headers,
        json={"status": "APPROVED"}
    )
    assert forbidden_resp.status_code == 403
    
    # 3. Admin approves the volunteer request
    approve_resp = client.patch(
        f"/api/events/{event_id}/volunteers/{volunteer_entry_id}",
        headers=admin_headers,
        json={"status": "APPROVED"}
    )
    assert approve_resp.status_code == 200
    assert approve_resp.get_json()["status"] in ["APPROVED", "ACTIVE"]
    
    # 4. Verify that the update is persisted in the volunteers listing
    list_resp = client.get(
        f"/api/events/{event_id}/volunteers",
        headers=student_headers
    )
    assert list_resp.status_code == 200
    updated_volunteers = list_resp.get_json()
    
    target_vol = next(item for item in updated_volunteers if item["id"] == volunteer_entry_id)
    assert target_vol["status"] in ["APPROVED", "ACTIVE"]
