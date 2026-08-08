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

    events = db.relationship('Event', backref='venue', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.venue_name,
            'location': self.venue_location,
            'type': self.venue_type,
            'capacity': self.capacity,
            'availabilityStatus': self.availability_status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organizer_type = db.Column(db.String(20), nullable=False, default='CLUB') # 'CLUB' or 'GENERAL'
    reservation_status = db.Column(db.String(30), nullable=False, default='RESERVED') # 'RESERVED', 'PENDING', 'RELEASED', 'NONE'
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
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

    club = db.relationship('Club', backref='events', lazy=True)
    creator = db.relationship('User', lazy=True, foreign_keys=[created_by])
    schedules = db.relationship('EventScheduleItem', backref='event', lazy=True, cascade='all, delete-orphan')
    announcements = db.relationship('EventAnnouncement', backref='event', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('EventRegistration', backref='event', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('EventAttendance', backref='event', lazy=True, cascade='all, delete-orphan')
    prizes = db.relationship('EventPrize', backref='event', lazy=True, cascade='all, delete-orphan')
    organizers = db.relationship('EventOrganizer', backref='event', lazy=True, cascade='all, delete-orphan')
    volunteers = db.relationship('EventVolunteer', backref='event', lazy=True, cascade='all, delete-orphan')

    def _creator_name(self):
        if self.creator and self.creator.student_profile:
            return self.creator.student_profile.full_name
        if self.creator and self.creator.faculty_profile:
            return self.creator.faculty_profile.full_name
        return None

    @property
    def computed_organizer_type(self):
        if self.organizer_type:
            return self.organizer_type.upper()
        return 'CLUB' if self.club_id else 'GENERAL'

    @property
    def event_type(self):
        return 'CLUB_EVENT' if self.computed_organizer_type == 'CLUB' else 'GENERAL_EVENT'

    @property
    def computed_reservation_status(self):
        status_upper = (self.event_status or '').upper()
        if status_upper in ['CANCELLED', 'CLOSED']:
            return 'RELEASED'
        if not self.venue_id:
            return 'NONE'
        return (self.reservation_status or 'RESERVED').upper()

    @property
    def computed_status(self):
        status_upper = (self.event_status or '').upper()
        if status_upper == 'CANCELLED':
            return 'Cancelled'
        if status_upper in ['COMPLETED', 'CLOSED']:
            return 'Completed'
        
        today = datetime.utcnow().date()
        if self.end_date and today > self.end_date:
            return 'Completed'
        elif self.start_date and today < self.start_date:
            return 'Scheduled'
        else:
            return 'Live'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.event_name,
            'description': self.event_description,
            'status': self.computed_status.upper() if self.computed_status else (self.event_status.upper() if self.event_status else 'SCHEDULED'),
            'rawStatus': self.event_status,
            'organizerType': self.computed_organizer_type,
            'eventType': self.event_type,
            'reservationStatus': self.computed_reservation_status,
            'reservedAt': self.reserved_at.isoformat() if self.reserved_at else None,
            'clubId': self.club_id,
            'clubName': self.club.club_name if self.club else 'General / Institutional',
            'club': self.club.club_name if self.club else 'General / Institutional',
            'venueId': self.venue_id,
            'venueName': self.venue.venue_name if self.venue else None,
            'venueLocation': self.venue.venue_location if self.venue else None,
            'venueCapacity': self.venue.capacity if self.venue else None,
            'venueType': self.venue.venue_type if self.venue else None,
            'createdBy': self.created_by,
            'createdByName': self._creator_name(),
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'startTime': self.start_time.strftime('%H:%M') if self.start_time else None,
            'endTime': self.end_time.strftime('%H:%M') if self.end_time else None,
            'capacity': self.capacity,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'schedule': [item.to_dict() for item in self.schedules],
            'announcements': [item.to_dict() for item in self.announcements],
            'registrations': [item.to_dict() for item in self.registrations],
            'attendance': [item.to_dict() for item in self.attendance_records],
            'prizes': [item.to_dict() for item in self.prizes],
            'organizers': [item.to_dict() for item in self.organizers],
            'volunteers': [item.to_dict() for item in self.volunteers],
        }


class EventScheduleItem(db.Model):
    __tablename__ = 'event_schedule_items'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    schedule_time = db.Column(db.String(20), nullable=False)
    activity = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'time': self.schedule_time,
            'activity': self.activity,
        }


class EventAnnouncement(db.Model):
    __tablename__ = 'event_announcements'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'date': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='uq_event_registration'),)

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registration_status = db.Column(db.String(30), nullable=False, default='REGISTERED')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'eventId': self.event_id,
            'userId': self.user_id,
            'userName': self.user.student_profile.full_name if self.user and self.user.student_profile else (
                self.user.faculty_profile.full_name if self.user and self.user.faculty_profile else None
            ),
            'status': self.registration_status,
            'registeredAt': self.registered_at.isoformat() if self.registered_at else None,
        }


class EventAttendance(db.Model):
    __tablename__ = 'event_attendance'
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='uq_event_attendance'),)

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attendance_status = db.Column(db.String(20), nullable=False, default='PRESENT')
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'eventId': self.event_id,
            'userId': self.user_id,
            'userName': self.user.student_profile.full_name if self.user and self.user.student_profile else (
                self.user.faculty_profile.full_name if self.user and self.user.faculty_profile else None
            ),
            'status': self.attendance_status.title(),
            'markedAt': self.marked_at.isoformat() if self.marked_at else None,
        }


class EventPrize(db.Model):
    __tablename__ = 'event_prizes'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    winner_name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'winnerName': self.winner_name,
            'description': self.description,
            'awardedAt': self.awarded_at.isoformat() if self.awarded_at else None,
        }


class EventOrganizer(db.Model):
    __tablename__ = 'event_organizers'
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='uq_event_organizer'),)

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organizer_role = db.Column(db.String(50), nullable=False, default='ORGANIZER')
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'eventId': self.event_id,
            'userId': self.user_id,
            'userName': self.user.student_profile.full_name if self.user and self.user.student_profile else (
                self.user.faculty_profile.full_name if self.user and self.user.faculty_profile else None
            ),
            'role': self.organizer_role,
            'assignedAt': self.assigned_at.isoformat() if self.assigned_at else None,
        }


class EventVolunteer(db.Model):
    __tablename__ = 'event_volunteers'
    __table_args__ = (db.UniqueConstraint('event_id', 'user_id', name='uq_event_volunteer'),)

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    volunteer_status = db.Column(db.String(30), nullable=False, default='PENDING')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'eventId': self.event_id,
            'userId': self.user_id,
            'userName': self.user.student_profile.full_name if self.user and self.user.student_profile else (
                self.user.faculty_profile.full_name if self.user and self.user.faculty_profile else None
            ),
            'status': self.volunteer_status,
            'requestedAt': self.requested_at.isoformat() if self.requested_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
