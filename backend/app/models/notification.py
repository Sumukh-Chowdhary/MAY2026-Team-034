from datetime import datetime
from app.models import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index = True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50),nullable=False,default='GENERAL')
    is_read = db.Column(db.Boolean, default=False)
    reference_url = db.Column(db.String(255), nullable=True)
    entity_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'title': self.title,
            'message': self.message,
            'type':self.type,
            'isRead': self.is_read,
            'referenceUrl': self.reference_url,
            'entityId':self.entity_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
