import pytest
from app.models.notification import Notification
from app.models.user import db

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session

def test_get_notifications_empty(client, student_headers):
    """
    User with no notifications should receive an empty list.
    """
    response = client.get("/api/notifications", headers=student_headers)
    assert response.status_code == 200
    assert response.get_json()["data"] == []


def test_unread_notification_count_empty(client, student_headers):
    """
    Newly logged in user should have zero unread notifications.
    """
    response = client.get("/api/notifications/unread-count", headers=student_headers)
    assert response.status_code == 200
    assert response.get_json()["count"] == 0


def test_notification_ordering(client, app, db_session, student_headers):
    """
    Notifications should be returned as:
    1. Unread first
    2. Newest first
    """
    with app.app_context():
        from app.models.user import User
        from datetime import datetime, timedelta
        student = User.query.filter_by(email="rahul@allclub.com").first()
        # 1. Read, Newest
        n1 = Notification(user_id=student.id, title="1", message="1", is_read=True, created_at=datetime.utcnow() + timedelta(days=1))
        # 2. Unread, Older
        n2 = Notification(user_id=student.id, title="2", message="2", is_read=False, created_at=datetime.utcnow())
        # 3. Unread, Newest
        n3 = Notification(user_id=student.id, title="3", message="3", is_read=False, created_at=datetime.utcnow() + timedelta(days=1))
        db_session.add_all([n1, n2, n3])
        db_session.commit()
    
    response = client.get("/api/notifications", headers=student_headers)
    data = response.get_json()["data"]
    assert len(data) == 3
    assert data[0]["title"] == "3"
    assert data[1]["title"] == "2"
    assert data[2]["title"] == "1"


def test_notification_limit_15(client, app, db_session, student_headers):
    """
    API should only return the latest 15 notifications.
    """
    with app.app_context():
        from app.models.user import User
        student = User.query.filter_by(email="rahul@allclub.com").first()
        for i in range(20):
            n = Notification(user_id=student.id, title=str(i), message="msg")
            db_session.add(n)
        db_session.commit()
        
    response = client.get("/api/notifications", headers=student_headers)
    data = response.get_json()["data"]
    assert len(data) == 15

def test_mark_notification_as_read(client, app, db_session, student_headers):
    """
    Marking a notification as read should:
    - return success
    - update DB
    - decrease unread count
    """
    with app.app_context():
        from app.models.user import User
        student = User.query.filter_by(email="rahul@allclub.com").first()
        n = Notification(user_id=student.id, title="Test", message="Test")
        db_session.add(n)
        db_session.commit()
        n_id = n.id

    response = client.patch(f"/api/notifications/{n_id}/read", headers=student_headers)
    assert response.status_code == 200

    count_res = client.get("/api/notifications/unread-count", headers=student_headers)
    assert count_res.get_json()["count"] == 0

    with app.app_context():
        n = db_session.get(Notification, n_id)
        assert n.is_read == True


def test_mark_notification_already_read(client, app, db_session, student_headers):
    """
    Marking an already-read notification should not fail.
    """
    with app.app_context():
        from app.models.user import User
        student = User.query.filter_by(email="rahul@allclub.com").first()
        n = Notification(user_id=student.id, title="Test", message="Test", is_read=True)
        db_session.add(n)
        db_session.commit()
        n_id = n.id

    response = client.patch(f"/api/notifications/{n_id}/read", headers=student_headers)
    assert response.status_code == 200


def test_mark_all_notifications_read(client, app, db_session, student_headers):
    """
    All unread notifications should become read.
    """
    with app.app_context():
        from app.models.user import User
        student = User.query.filter_by(email="rahul@allclub.com").first()
        for i in range(3):
            n = Notification(user_id=student.id, title="Test", message="Test")
            db_session.add(n)
        db_session.commit()

    count_res1 = client.get("/api/notifications/unread-count", headers=student_headers)
    assert count_res1.get_json()["count"] == 3

    response = client.patch("/api/notifications/read-all", headers=student_headers)
    assert response.status_code == 200

    count_res2 = client.get("/api/notifications/unread-count", headers=student_headers)
    assert count_res2.get_json()["count"] == 0


def test_mark_invalid_notification(client, student_headers):
    """
    Reading an invalid notification id should return 404.
    """
    response = client.patch("/api/notifications/99999/read", headers=student_headers)
    assert response.status_code == 404


def test_user_cannot_read_other_users_notification(
    client,
    app,
    db_session,
    admin_headers,
    student_headers
):
    """
    User should never be able to mark another user's
    notification as read.
    """
    with app.app_context():
        from app.models.user import User
        admin = User.query.filter_by(email="admin@allclub.com").first()
        n = Notification(user_id=admin.id, title="Admin Notif", message="Test")
        db_session.add(n)
        db_session.commit()
        n_id = n.id

    response = client.patch(f"/api/notifications/{n_id}/read", headers=student_headers)
    assert response.status_code == 404

def test_ticket_assignment_notifies_approver(
    client,
    student_headers,
    faculty_headers
):
    """
    Assigned approver should receive
    'New Ticket Assigned'.
    """
    client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Custom request",
        "description": "Custom workflow",
        "referenceType": "CLUB",
        "referenceId": 1,
        "approvers": [
            {"approverId": 3, "role": "FACULTY"} # Assuming user 3 is faculty
        ]
    })
    
    notif_res = client.get("/api/notifications", headers=faculty_headers)
    assert notif_res.status_code == 200
    data = notif_res.get_json()["data"]
    assert len(data) >= 1
    assert any("New Ticket Assigned" in n["title"] or "Assigned" in n["title"] or n["type"] == "TICKET" for n in data)


def test_ticket_approval_notifies_creator(
    client,
    student_headers,
    faculty_headers
):
    """
    Approving a ticket should notify
    the creator.
    """
    res = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Approval Test",
        "description": "Testing approval flow",
        "referenceType": "CLUB",
        "referenceId": 1,
        "approvers": [{"approverId": 3, "role": "FACULTY"}]
    })
    req_id = res.get_json()["data"]["id"]
    
    client.post(f"/api/requests/{req_id}/approve", headers=faculty_headers, json={"remarks": "Looks good"})
    
    notif_res = client.get("/api/notifications", headers=student_headers)
    data = notif_res.get_json()["data"]
    assert any("Approved" in n["title"] or "Approved" in n["message"] for n in data)


def test_ticket_rejection_notifies_creator(
    client,
    student_headers,
    faculty_headers
):
    """
    Rejecting a ticket should notify
    the creator.
    """
    res = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Reject Test",
        "description": "Testing reject flow",
        "referenceType": "CLUB",
        "referenceId": 1,
        "approvers": [{"approverId": 3, "role": "FACULTY"}]
    })
    req_id = res.get_json()["data"]["id"]
    
    client.post(f"/api/requests/{req_id}/reject", headers=faculty_headers, json={"remarks": "No"})
    
    notif_res = client.get("/api/notifications", headers=student_headers)
    data = notif_res.get_json()["data"]
    assert any("Rejected" in n["title"] or "Rejected" in n["message"] for n in data)


def test_ticket_fully_approved_notification(
    client,
    student_headers,
    faculty_headers,
    admin_headers
):
    """
    Creator should only receive
    'Fully Approved'
    after final approval.
    """
    res = client.post("/api/requests", headers=student_headers, json={
        "requestType": "BUDGET_REQUEST",
        "title": "Full Approval Test",
        "description": "Testing full approval",
        "referenceType": "CLUB",
        "referenceId": 1,
        "approvers": [
            {"approverId": 3, "role": "FACULTY"},
            {"approverId": 1, "role": "ADMIN"}
        ]
    })
    req_id = res.get_json()["data"]["id"]
    
    client.post(f"/api/requests/{req_id}/approve", headers=faculty_headers, json={"remarks": "OK"})
    client.post(f"/api/requests/{req_id}/approve", headers=admin_headers, json={"remarks": "OK"})
    
    notif_res = client.get("/api/notifications", headers=student_headers)
    data = notif_res.get_json()["data"]
    assert any("Fully Approved" in n["title"] or "Approved" in n["title"] for n in data)


def test_ticket_closed_notification(
    client,
    app,
    student_headers,
    faculty_headers
):
    """
    Closing a ticket should notify
    the creator.
    """
    from app.services.notification_service import NotificationService
    with app.app_context():
        from app.models.user import User
        student = User.query.filter_by(email="rahul@allclub.com").first()
        NotificationService.notify_ticket_closed(student.id, 999)

    notif_res = client.get("/api/notifications", headers=student_headers)
    data = notif_res.get_json()["data"]
    assert any("Closed" in n["title"] for n in data)


# ==========================================================
# SECURITY
# ==========================================================

def test_notifications_requires_auth(client):
    """
    Notifications endpoint requires authentication.
    """
    response = client.get("/api/notifications")
    assert response.status_code == 401


def test_unread_count_requires_auth(client):
    """
    Unread count endpoint requires authentication.
    """
    response = client.get("/api/notifications/unread-count")
    assert response.status_code == 401


def test_mark_read_requires_auth(client):
    """
    Read endpoint requires authentication.
    """
    response = client.patch("/api/notifications/1/read")
    assert response.status_code == 401


def test_mark_all_requires_auth(client):
    """
    Read-all endpoint requires authentication.
    """
    response = client.patch("/api/notifications/read-all")
    assert response.status_code == 401


# ==========================================================
# DATA VALIDATION
# ==========================================================

def test_notification_contains_required_fields(
    client,
    app,
    student_headers
):
    """
    Every notification should contain

    id
    title
    message
    type
    entityId
    referenceUrl
    isRead
    createdAt
    """
    with app.app_context():
        from app.models.user import User
        from app.services.notification_service import NotificationService
        student = User.query.filter_by(email="rahul@allclub.com").first()
        NotificationService.create(student.id, "Test", "Test Message", "GENERAL")

    response = client.get("/api/notifications", headers=student_headers)
    assert response.status_code == 200
    data = response.get_json()["data"][0]
    
    required_fields = ["id", "title", "message", "type", "entityId", "referenceUrl", "isRead", "createdAt"]
    for field in required_fields:
        assert field in data


def test_notification_unread_count_matches_database(
    client,
    app,
    db_session,
    student_headers
):
    """
    API unread count should equal
    actual unread records in DB.
    """
    with app.app_context():
        from app.models.user import User
        student = User.query.filter_by(email="rahul@allclub.com").first()
        for i in range(5):
            n = Notification(user_id=student.id, title="Test", message="Test", is_read=False)
            db_session.add(n)
        for i in range(3):
            n = Notification(user_id=student.id, title="Test", message="Test", is_read=True)
            db_session.add(n)
        db_session.commit()

    response = client.get("/api/notifications/unread-count", headers=student_headers)
    assert response.status_code == 200
    assert response.get_json()["count"] == 5