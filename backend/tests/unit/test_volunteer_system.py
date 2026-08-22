import pytest
from datetime import datetime, timedelta
from app.models import db
from app.models.user import User
from app.models.tickets import Request
from app.models.events import Event, EventVolunteer, EventVolunteerPosition
from app.models.club import Club, ClubFaculty, ClubMembership

def test_get_volunteer_positions(client):
    """Event returns DB-backed volunteer positions with capacities."""
    login_res = client.post("/api/auth/login", json={"username": "Y24CS001", "password": "student123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/events/1/volunteer-positions", headers=headers)
    assert res.status_code == 200
    positions = res.get_json()
    assert len(positions) >= 1
    p_names = [p["positionName"] for p in positions]
    assert "Registration Desk" in p_names
    assert "Technical Support" in p_names

def test_volunteer_application_workflow(client, app):
    """Student applies as volunteer -> Ticket routed to Club Faculty Coordinator -> Approval activates 3-day role."""
    # 1. Login as student (Rahul - ACTIVE member of AI/Coding Club)
    login_res = client.post("/api/auth/login", json={"username": "Y24CS001", "password": "student123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        EventVolunteer.query.filter_by(event_id=1, user_id=24).delete()
        db.session.commit()

    # Apply for volunteer position 'Registration Desk' on Event 1
    apply_res = client.post(
        "/api/events/1/volunteer-apply",
        headers=headers,
        json={"positionName": "Registration Desk"}
    )
    assert apply_res.status_code == 201
    data = apply_res.get_json()
    assert data["success"] is True
    ticket_id = data["ticket"]["id"]
    vol_id = data["data"]["id"]

    # Verify ticket routed to Club Faculty Coordinator
    with app.app_context():
        req = Request.query.get(ticket_id)
        assert req.request_type == "VOLUNTEER"
        assert len(req.approvals) == 1
        fac_id = req.approvals[0].approver_id
        fac_user = User.query.get(fac_id)
        assert fac_user.role.name == "FACULTY"
        fac_email = fac_user.email
        requester_id = req.requester_id

    # 2. Login as Faculty Coordinator to approve ticket
    fac_login = client.post("/api/auth/login", json={"email": fac_email, "password": "faculty123"})
    fac_token = fac_login.get_json()["token"]
    fac_headers = {"Authorization": f"Bearer {fac_token}"}

    appr_res = client.post(f"/api/requests/{ticket_id}/approve", headers=fac_headers)
    assert appr_res.status_code == 200

    # 3. Check student roles endpoint returns active volunteer role with 3-day duration
    roles_res = client.get(f"/api/assignment-tickets/user/{requester_id}", headers=headers)
    assert roles_res.status_code == 200
    roles_data = roles_res.get_json()["data"]
    active_roles = roles_data["active"]
    vol_role = next(r for r in active_roles if "VOLUNTEER" in r["assignmentRole"].upper() or "Volunteer" in r["assignmentRole"])
    assert vol_role["status"] == "ACTIVE"

def test_legacy_student_cannot_apply_as_volunteer(client, app):
    """LEGACY student cannot apply for volunteer positions."""
    with app.app_context():
        leg_user = User.query.filter_by(account_status="LEGACY").first()
        reg_id = leg_user.student_profile.roll_no

    login_res = client.post("/api/auth/login", json={"username": reg_id, "password": "student123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/events/1/volunteer-apply", headers=headers, json={"positionName": "Registration Desk"})
    assert res.status_code == 403
    err_msg = res.get_json()["error"]
    assert "Legacy" in err_msg or "Graduated" in err_msg

def test_full_volunteer_position_rejected(client, app):
    """Position with filled capacity cannot accept new applications."""
    with app.app_context():
        EventVolunteer.query.filter_by(event_id=1, user_id=24).delete()
        # Set max capacity of Photography position on event 1 to 0
        pos = EventVolunteerPosition.query.filter_by(event_id=1, position_name="Photography").first()
        if not pos:
            pos = EventVolunteerPosition(event_id=1, position_name="Photography", max_capacity=0)
            db.session.add(pos)
        else:
            pos.max_capacity = 0
        db.session.commit()

    login_res = client.post("/api/auth/login", json={"username": "Y24CS001", "password": "student123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/events/1/volunteer-apply", headers=headers, json={"positionName": "Photography"})
    assert res.status_code == 400
    assert "FULL" in res.get_json()["error"]
