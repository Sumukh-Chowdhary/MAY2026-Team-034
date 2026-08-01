import pytest
from app.models.notification import Notification
from app.models.user import db

def test_notification_lifecycle_integration(client, app, student_headers):
    # 1. Trigger / Create a notification in database for student user (email "rahul@allclub.com")
    with app.app_context():
        from app.models.user import User
        student = User.query.filter_by(email="rahul@allclub.com").first()
        assert student is not None
        
        notification = Notification(
            user_id=student.id,
            title="Integration Alert",
            message="This is a real-time integration test notification",
            type="ALERT",
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        notification_id = notification.id

    # 2. Get unread count via REST API
    count_response = client.get("/api/notifications/unread-count", headers=student_headers)
    assert count_response.status_code == 200
    assert count_response.get_json()["count"] == 1

    # 3. Retrieve notifications list via REST API
    list_response = client.get("/api/notifications", headers=student_headers)
    assert list_response.status_code == 200
    notifications = list_response.get_json()["data"]
    
    assert len(notifications) >= 1
    target_notification = next(n for n in notifications if n["id"] == notification_id)
    assert target_notification["title"] == "Integration Alert"
    assert target_notification["isRead"] is False

    # 4. Mark notification as read
    read_response = client.patch(f"/api/notifications/{notification_id}/read", headers=student_headers)
    assert read_response.status_code == 200

    # 5. Verify unread count is updated
    count_response_after = client.get("/api/notifications/unread-count", headers=student_headers)
    assert count_response_after.status_code == 200
    assert count_response_after.get_json()["count"] == 0
