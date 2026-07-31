from datetime import datetime
from app.models import db


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String(120), unique=True, nullable=False)
    venue_location = db.Column(db.String(255), nullable=False)
    venue_type = db.Column(db.String(80), nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    availability_status = db.Column(db.String(30), nullable=False, default='AVAILABLE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = db.relationship(
        'Event', backref='venue', lazy=True, cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.venue_name,
            'location': self.venue_location,
            'type': self.venue_type,
            'capacity': self.capacity,
            'availabilityStatus': self.availability_status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_name = db.Column(db.String(150), nullable=False)
    event_description = db.Column(db.Text, nullable=True)
    event_status = db.Column(db.String(40), nullable=False, default='SCHEDULED')
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship(
    'User',
    lazy=True,
    foreign_keys=[created_by]
    )

    schedules = db.relationship(
        "EventSchedule",
        backref="event",
        lazy=True,
        cascade="all, delete-orphan"
    )

    announcements = db.relationship(
        "Announcement",
        backref="event",
        lazy=True,
        cascade="all, delete-orphan"
    )

    registrations = db.relationship(
        "EventRegistration",
        backref="event",
        lazy=True,
        cascade="all, delete-orphan"
    )

    attendance = db.relationship(
        "Attendance",
        backref="event",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.event_name,
            'description': self.event_description,
            'status': self.event_status,
            'clubId': self.club_id,
            'clubName': self.club.club_name if self.club else None,
            'venueId': self.venue_id,
            'venueName': self.venue.venue_name if self.venue else None,
            'createdBy': self.created_by,
            'createdByName': self.creator.student_profile.full_name if self.creator and self.creator.student_profile else (
                self.creator.faculty_profile.full_name if self.creator and self.creator.faculty_profile else None
            ),
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'startTime': self.start_time.strftime('%H:%M') if self.start_time else None,
            'endTime': self.end_time.strftime('%H:%M') if self.end_time else None,
            'capacity': self.capacity,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


