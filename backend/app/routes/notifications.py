from flask import g, Blueprint
from app.utils.auth_jwt import jwt_required

from app.services.notification_service import NotificationService

notifications_bp = Blueprint("notifications", __name__,url_prefix='/api/notifications')

@notifications_bp.get("")
@jwt_required
def get_notifications():
    user_id = g.current_user.id

    notifications = NotificationService.get_user_notifications(user_id)
    return {
        "success": True,
        "data":[
            n.to_dict() for n in notifications
        ]
    }

@notifications_bp.get("/unread-count")
@jwt_required
def unread_count():
    user_id = g.current_user.id
    return {
        "success":True,
        "count":NotificationService.unread_count(user_id)
    }

@notifications_bp.patch("/<int:notification_id>/read")
@jwt_required
def mark_read(notification_id):
    user_id = g.current_user.id
    notification = NotificationService.mark_read(notification_id,user_id)

    if not notification:
        return {
            "success": False,
            "message":"Notification not found"
        },404

    return {
        "success":True
    }

@notifications_bp.patch("/read-all")
@jwt_required
def mark_all():
    user_id = g.current_user.id
    NotificationService.mark_all_read(user_id)

    return {
        "success": True
    }