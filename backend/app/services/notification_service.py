from app.models import db
from app.models.notification import Notification
from app.extensions import socketio

class NotificationService:
    @staticmethod
    def create(user_id, title, message, notification_type, entity_id=None, reference_url=None):
        """Creates a notification and emits a socket event."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            entity_id=entity_id,
            reference_url=reference_url
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Emit real-time update
        room = f"user_{user_id}"
        socketio.emit("new_notification", notification.to_dict(), room=room)
        
        return notification

    @staticmethod
    def get_user_notifications(user_id, limit=15):
        return Notification.query.filter_by(user_id=user_id).order_by(
            Notification.is_read.asc(),
            Notification.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def unread_count(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_read(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
        return notification

    @staticmethod
    def mark_all_read(user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
        db.session.commit()

    @staticmethod
    def notify_ticket_created(creator_id, ticket_id, approver_ids=None):
        # Notify Creator
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Created",
            message=f"Your ticket #{ticket_id} has been submitted.",
            notification_type="TICKET",
            entity_id=ticket_id,
            reference_url=f"/student/tickets/{ticket_id}"
        )
        
        # Notify Approvers
        if approver_ids:
            for approver_id in approver_ids:
                NotificationService.create(
                    user_id=approver_id,
                    title="New Ticket Assigned",
                    message=f"You have been assigned to review Ticket #{ticket_id}.",
                    notification_type="TICKET",
                    entity_id=ticket_id,
                    reference_url=f"/faculty/requests/{ticket_id}"
                )

    @staticmethod
    def notify_ticket_approved(creator_id, ticket_id, approver_name):
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Approved",
            message=f"{approver_name} approved your ticket #{ticket_id}.",
            notification_type="TICKET",
            entity_id=ticket_id,
            reference_url=f"/student/tickets/{ticket_id}"
        )

    @staticmethod
    def notify_ticket_rejected(creator_id, ticket_id, approver_name):
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Rejected",
            message=f"{approver_name} rejected your ticket #{ticket_id}.",
            notification_type="TICKET",
            entity_id=ticket_id,
            reference_url=f"/student/tickets/{ticket_id}"
        )

    @staticmethod
    def notify_ticket_fully_approved(creator_id, ticket_id):
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Fully Approved",
            message=f"Your ticket #{ticket_id} has been fully approved.",
            notification_type="TICKET",
            entity_id=ticket_id,
            reference_url=f"/student/tickets/{ticket_id}"
        )

    @staticmethod
    def notify_ticket_closed(creator_id, ticket_id):
        NotificationService.create(
            user_id=creator_id,
            title="Ticket Closed",
            message=f"Your ticket #{ticket_id} has been closed.",
            notification_type="TICKET",
            entity_id=ticket_id,
            reference_url=f"/student/tickets/{ticket_id}"
        )

    @staticmethod
    def notify_club_created(creator_id, club_name, club_id):
        NotificationService.create(
            user_id=creator_id,
            title="Club Created",
            message=f"Your club '{club_name}' has been created.",
            notification_type="CLUB",
            entity_id=club_id,
            reference_url=f"/clubs/{club_id}"
        )