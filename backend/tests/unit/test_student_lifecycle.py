import pytest
from app.models import db, User, StudentProfile, EventRegistration, EventAttendance, ClubMembership, Event
from app.utils.registration_id import generate_registration_id, validate_registration_id, get_branch_code, parse_registration_id

# 1. Registration ID generation
def test_registration_id_generation():
    reg_id1 = generate_registration_id(2026, "Computer Science", 1)
    assert reg_id1 == "Y26CS001"
    
    reg_id2 = generate_registration_id(2025, "Electronics", 14)
    assert reg_id2 == "Y25EC014"

    assert validate_registration_id("Y26CS001") is True

# 2. Registration ID uniqueness
def test_registration_id_uniqueness(app):
    with app.app_context():
        dups = db.session.query(StudentProfile.roll_no).group_by(StudentProfile.roll_no).having(db.func.count(StudentProfile.roll_no) > 1).all()
        assert len(dups) == 0

# 3. Invalid branch code fallback handling
def test_invalid_branch_code_fallback():
    code = get_branch_code("Unknown Specialization Department")
    assert len(code) == 2
    assert code.isupper()
    reg_id = generate_registration_id(2026, "Unknown Dept", 99)
    assert reg_id.startswith("Y26")

# 4. Student login using new registration ID
def test_student_login_with_registration_id(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "Y24CS001",
            "password": "student123"
        }
    )
    assert response.status_code == 200
    assert "token" in response.get_json()

def test_student_login_with_email_disabled(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "rahul@allclub.com",
            "password": "student123"
        }
    )
    assert response.status_code == 400
    assert "Students must log in using their Registration ID" in response.get_json()["error"]

# 5. Admin login still working
def test_admin_login_still_working(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin@allclub.com",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "ADMIN"

# 6. Faculty login still working
def test_faculty_login_still_working(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "FAC001",
            "password": "faculty123"
        }
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "FACULTY"

# 7. Active user display
def test_active_user_display(client):
    # Login as active student using Registration ID
    login_res = client.post("/api/auth/login", json={"username": "Y24CS001", "password": "student123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/users", headers=headers)
    assert res.status_code == 200
    users = res.get_json()
    rahul = next(u for u in users if u["email"] == "rahul@allclub.com")
    assert rahul["status"] == "ACTIVE"
    assert rahul["isLegacy"] is False
    assert rahul["registerNumber"].startswith("Y")

# 8. Legacy user display
def test_legacy_user_display(client, app):
    with app.app_context():
        leg_user = User.query.filter_by(account_status="LEGACY").first()
        reg_id = leg_user.student_profile.roll_no

    login_res = client.post("/api/auth/login", json={"username": reg_id, "password": "student123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/users", headers=headers)
    assert res.status_code == 200
    users = res.get_json()
    legacy_u = next(u for u in users if u["id"] == leg_user.id)
    assert legacy_u["status"] == "LEGACY"
    assert legacy_u["isLegacy"] is True

# 9. Admin Legacy Users page filtering endpoint
def test_admin_legacy_users_page_filtering(client):
    login_res = client.post("/api/auth/login", json={"username": "admin@allclub.com", "password": "admin123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/users", headers=headers)
    assert res.status_code == 200
    users = res.get_json()
    legacy_count = sum(1 for u in users if u["status"] == "LEGACY")
    assert legacy_count >= 1

# 10. Club Legacy Members
def test_club_legacy_members_response(client):
    login_res = client.post("/api/auth/login", json={"username": "admin@allclub.com", "password": "admin123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/student/clubs/1", headers=headers)
    assert res.status_code == 200

# 11. Historical event records after graduation
def test_historical_event_records_after_graduation(client, app):
    with app.app_context():
        # Get legacy user
        leg_user = User.query.filter_by(account_status="LEGACY").first()
        event = Event.query.first()
        # Verify event creator or user details retain name and reg id
        assert leg_user.student_profile.full_name is not None
        assert leg_user.student_profile.roll_no.startswith("Y")

# 12. Historical attendance after graduation
def test_historical_attendance_after_graduation(client, app):
    with app.app_context():
        leg_user = User.query.filter_by(account_status="LEGACY").first()
        att = EventAttendance.query.filter_by(user_id=leg_user.id).first()
        if att:
            att_dict = att.to_dict()
            assert att_dict["userName"] == leg_user.student_profile.full_name
            assert att_dict["registerNumber"] == leg_user.student_profile.roll_no

# 13. Historical registrations after graduation
def test_historical_registrations_after_graduation(client, app):
    with app.app_context():
        leg_user = User.query.filter_by(account_status="LEGACY").first()
        reg = EventRegistration.query.filter_by(user_id=leg_user.id).first()
        if reg:
            reg_dict = reg.to_dict()
            assert reg_dict["userName"] == leg_user.student_profile.full_name
            assert reg_dict["registerNumber"] == leg_user.student_profile.roll_no

# 14. Legacy users cannot perform restricted new-student actions
def test_legacy_user_action_restrictions(client, app):
    with app.app_context():
        leg_user = User.query.filter_by(account_status="LEGACY").first()
        reg_id = leg_user.student_profile.roll_no

    login_res = client.post("/api/auth/login", json={"username": reg_id, "password": "student123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Cannot join club
    res1 = client.post("/api/student/clubs/1/join", headers=headers)
    assert res1.status_code == 403

    # Cannot register for event
    res2 = client.post("/api/events/1/register", headers=headers)
    assert res2.status_code == 403

    # Cannot submit request
    res3 = client.post("/api/requests", headers=headers, json={"title": "Test", "description": "Test", "requestType": "EVENT_PROPOSAL"})
    assert res3.status_code == 403

# 15. Profile modal works for active and legacy users
def test_profile_endpoint_for_active_and_legacy_users(client, app):
    login_res = client.post("/api/auth/login", json={"username": "admin@allclub.com", "password": "admin123"})
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    with app.app_context():
        act_user = User.query.filter_by(account_status="ACTIVE", role_id=3).first()
        leg_user = User.query.filter_by(account_status="LEGACY").first()

    # Active profile view
    res_act = client.get(f"/api/users/{act_user.id}", headers=headers)
    assert res_act.status_code == 200
    assert res_act.get_json()["status"] == "ACTIVE"

    # Legacy profile view
    res_leg = client.get(f"/api/users/{leg_user.id}", headers=headers)
    assert res_leg.status_code == 200
    assert res_leg.get_json()["status"] == "LEGACY"
    assert res_leg.get_json()["isLegacy"] is True

# 16. Test explicit LEGACY student accounts (Rahul, Ananya, Vikram)
def test_explicit_legacy_student_accounts(client, app):
    legacy_regs = ["Y22CS001", "Y22EC004", "Y21ME002"]
    
    for reg_id in legacy_regs:
        # A. Login works
        login_res = client.post("/api/auth/login", json={"username": reg_id, "password": "student123"})
        assert login_res.status_code == 200
        token = login_res.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # B. Profile endpoint returns LEGACY status with valid registration details
        me_res = client.get("/api/users/me", headers=headers)
        assert me_res.status_code == 200
        data = me_res.get_json()
        assert data["registrationId"] == reg_id
        assert data["accountStatus"] == "LEGACY"
        assert data["isLegacy"] is True

        # C. Restricted student actions return 403 Forbidden
        assert client.post("/api/student/clubs/1/join", headers=headers).status_code == 403
        assert client.post("/api/events/1/register", headers=headers).status_code == 403
        assert client.post("/api/requests", headers=headers, json={"title": "Test", "requestType": "EVENT_PROPOSAL"}).status_code == 403

        # D. Current active roles do not include expired/legacy roles
        roles_res = client.get("/api/student/roles/my-roles", headers=headers)
        if roles_res.status_code == 200:
            roles_data = roles_res.get_json()
            active_roles = roles_data.get("activeRoles", []) if isinstance(roles_data, dict) else roles_data
            assert len(active_roles) == 0
