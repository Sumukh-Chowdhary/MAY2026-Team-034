from app.models import db
from app.models.notification import Notification
from app.sockets import socketio

def create_notification(user_id, title, message, reference_url=None):
    """
    Creates a notification in the database and emits it via Socket.IO
    to the specific user's room.
    """
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            reference_url=reference_url
        )
        db.session.add(notification)
        db.session.commit()

        # Emit to user's personal room
        room = f"user_{user_id}"
        socketio.emit('new_notification', notification.to_dict(), to=room)
        
        return notification
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None
