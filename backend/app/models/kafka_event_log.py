from datetime import datetime
from app.models import db

class KafkaEventLog(db.Model):
    __tablename__ = "kafka_event_logs"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, nullable=True)

    kafka_partition = db.Column(db.Integer, nullable=False)
    kafka_offset = db.Column(db.Integer, nullable=False)

    processed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )