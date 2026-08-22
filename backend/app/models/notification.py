from datetime import datetime
from app.models import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False, default='GENERAL', index=True)
    entity_type = db.Column(db.String(50), nullable=True, index=True)
    entity_id = db.Column(db.Integer, nullable=True, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    context = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    reference_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        db.Index('ix_notification_user_unread', 'user_id', 'is_read', 'created_at'),
    )

    actor = db.relationship('User', foreign_keys=[actor_id])

    def to_dict(self):
        actor_name = None
        if self.actor:
            if hasattr(self.actor, 'student_profile') and self.actor.student_profile:
                actor_name = self.actor.student_profile.full_name
            elif hasattr(self.actor, 'faculty_profile') and self.actor.faculty_profile:
                actor_name = self.actor.faculty_profile.full_name

        return {
            'id': self.id,
            'userId': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'entityType': self.entity_type,
            'entityId': self.entity_id,
            'actorId': self.actor_id,
            'actorName': actor_name,
            'context': self.context,
            'isRead': self.is_read,
            'referenceUrl': self.reference_url,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
