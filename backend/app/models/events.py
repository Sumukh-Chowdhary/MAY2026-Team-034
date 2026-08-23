from datetime import datetime
from app.models import db


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    venue_location = db.Column(db.String(255), nullable=False)
    venue_type = db.Column(db.String(80), nullable=True, index=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    availability_status = db.Column(db.String(30), nullable=False, default='AVAILABLE', index=True)
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
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=True, index=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    organizer_type = db.Column(db.String(20), nullable=False, default='CLUB', index=True) # 'CLUB' or 'GENERAL'
    reservation_status = db.Column(db.String(30), nullable=False, default='RESERVED') # 'RESERVED', 'PENDING', 'RELEASED', 'NONE'
    reserved_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_name = db.Column(db.String(150), nullable=False, index=True)
    event_description = db.Column(db.Text, nullable=True)
    event_status = db.Column(db.String(40), nullable=False, default='SCHEDULED', index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    event_format = db.Column(db.String(20), nullable=False, default='COMPETITION')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('ix_event_venue_dates', 'venue_id', 'start_date', 'end_date', 'event_status'),
        db.Index('ix_event_club_status', 'club_id', 'event_status'),
    )

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
            'eventFormat': (self.event_format or 'COMPETITION').upper(),
            'isCompetition': (self.event_format or 'COMPETITION').upper() == 'COMPETITION' or len(self.sessions) > 1 or len(self.prizes) > 0,
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
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
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
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    created_by = db.relationship('User', foreign_keys=[created_by_id], lazy=True)

    def to_dict(self):
        cb_sp = getattr(self.created_by, 'student_profile', None) if self.created_by else None
        cb_fp = getattr(self.created_by, 'faculty_profile', None) if self.created_by else None
        cb_name = cb_sp.full_name if cb_sp else (cb_fp.full_name if cb_fp else getattr(self.created_by, 'username', 'Organizer'))

        return {
            'id': self.id,
            'eventId': self.event_id,
            'title': self.title,
            'message': self.message,
            'createdById': self.created_by_id,
            'createdByName': cb_name,
            'date': self.created_at.strftime('%Y-%m-%d') if self.created_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_event_registration'),
        db.Index('ix_event_registration_lookup', 'event_id', 'user_id', 'registration_status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    registration_status = db.Column(db.String(30), nullable=False, default='REGISTERED', index=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship('User', lazy=True)

    def to_dict(self):
        sp = self.user.student_profile if (self.user and hasattr(self.user, 'student_profile')) else None
        fp = self.user.faculty_profile if (self.user and hasattr(self.user, 'faculty_profile')) else None
        u_name = sp.full_name if sp else (fp.full_name if fp else (self.user.email if self.user else None))
        reg_id = (sp.registration_id or sp.roll_no) if sp else (fp.employee_id if fp else None)
        u_status = self.user.account_status if self.user else 'ACTIVE'

        return {
            'id': self.id,
            'eventId': self.event_id,
            'userId': self.user_id,
            'userName': u_name,
            'registerNumber': reg_id,
            'rollNumber': reg_id,
            'userStatus': u_status,
            'isLegacy': (u_status == 'LEGACY'),
            'status': self.registration_status,
            'registeredAt': self.registered_at.isoformat() if self.registered_at else None,
        }


class EventSession(db.Model):
    __tablename__ = 'event_sessions'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    round_number = db.Column(db.Integer, nullable=False, default=1, index=True)
    status = db.Column(db.String(20), nullable=False, default='UPCOMING', index=True)
    session_date = db.Column(db.Date, nullable=True, index=True)
    start_time = db.Column(db.String(30), nullable=True)
    end_time = db.Column(db.String(30), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('sessions', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        records = EventAttendance.query.filter_by(session_id=self.id).all()
        present_count = sum(1 for r in records if (r.attendance_status or '').upper() == 'PRESENT')
        absent_count = sum(1 for r in records if (r.attendance_status or '').upper() == 'ABSENT')
        total_count = len(records)
        shortlisted_count = ParticipantRoundStatus.query.filter_by(session_id=self.id, status='SHORTLISTED').count()
        eliminated_count = ParticipantRoundStatus.query.filter_by(session_id=self.id, status='ELIMINATED').count()

        # Parse linked round context stored in description as prefix
        linked_round_id = None
        linked_round_name = None
        clean_description = self.description or ''
        if clean_description.startswith('__linked_round__:'):
            try:
                meta_part, _, user_desc = clean_description.partition('|')
                _, _, rest = meta_part.partition(':')
                rid_str, _, rname = rest.partition(':')
                linked_round_id = int(rid_str)
                linked_round_name = rname
                clean_description = user_desc.strip()
            except Exception:
                pass

        return {
            'id': self.id,
            'eventId': self.event_id,
            'name': self.name,
            'roundNumber': self.round_number,
            'status': (self.status or 'UPCOMING').upper(),
            'sessionDate': self.session_date.isoformat() if self.session_date else None,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'description': clean_description,
            'linkedRoundId': linked_round_id,
            'linkedRoundName': linked_round_name,
            'presentCount': present_count,
            'absentCount': absent_count,
            'totalCount': total_count,
            'shortlistedCount': shortlisted_count,
            'eliminatedCount': eliminated_count,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }



class ParticipantRoundStatus(db.Model):
    __tablename__ = 'participant_round_statuses'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey('event_sessions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default='REGISTERED', index=True)
    reason = db.Column(db.Text, nullable=True)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('session_id', 'user_id', name='uq_prs_session_user'),
        db.Index('ix_prs_session_user_status', 'session_id', 'user_id', 'status'),
    )

    session = db.relationship('EventSession', backref=db.backref('round_statuses', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', foreign_keys=[user_id], lazy=True)
    updated_by = db.relationship('User', foreign_keys=[updated_by_id], lazy=True)

    def to_dict(self):
        sp = getattr(self.user, 'student_profile', None)
        fp = getattr(self.user, 'faculty_profile', None)
        u_name = sp.full_name if sp else (fp.full_name if fp else getattr(self.user, 'username', 'User'))
        reg_num = sp.roll_no if sp else (fp.employee_id if fp else 'N/A')
        ub_sp = getattr(self.updated_by, 'student_profile', None)
        ub_fp = getattr(self.updated_by, 'faculty_profile', None)
        ub_name = ub_sp.full_name if ub_sp else (ub_fp.full_name if ub_fp else getattr(self.updated_by, 'username', None))

        return {
            'id': self.id,
            'eventId': self.event_id,
            'sessionId': self.session_id,
            'roundName': self.session.name if self.session else None,
            'roundNumber': self.session.round_number if self.session else None,
            'userId': self.user_id,
            'userName': u_name,
            'userEmail': self.user.email if self.user else None,
            'registerNumber': reg_num,
            'status': self.status,
            'reason': self.reason,
            'updatedById': self.updated_by_id,
            'updatedByName': ub_name,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class EventAttendance(db.Model):
    __tablename__ = 'event_attendance'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    session_id = db.Column(db.Integer, db.ForeignKey('event_sessions.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    attendance_status = db.Column(db.String(20), nullable=False, default='PRESENT', index=True)
    marked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('ix_attendance_session_user', 'session_id', 'user_id'),
    )

    user = db.relationship('User', foreign_keys=[user_id], lazy=True)
    marked_by = db.relationship('User', foreign_keys=[marked_by_id], lazy=True)
    session = db.relationship('EventSession', backref=db.backref('attendance_records', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        student_prof = self.user.student_profile if (self.user and hasattr(self.user, 'student_profile')) else None
        faculty_prof = self.user.faculty_profile if (self.user and hasattr(self.user, 'faculty_profile')) else None
        
        marked_by_name = None
        if self.marked_by:
            mb_sp = getattr(self.marked_by, 'student_profile', None)
            mb_fp = getattr(self.marked_by, 'faculty_profile', None)
            marked_by_name = mb_sp.full_name if mb_sp else (mb_fp.full_name if mb_fp else getattr(self.marked_by, 'username', 'User'))

        user_name = student_prof.full_name if student_prof else (faculty_prof.full_name if faculty_prof else getattr(self.user, 'username', 'Participant'))

        return {
            'id': self.id,
            'eventId': self.event_id,
            'sessionId': self.session_id,
            'userId': self.user_id,
            'userName': user_name,
            'userEmail': self.user.email if self.user else None,
            'registerNumber': student_prof.roll_no if student_prof else (faculty_prof.employee_id if faculty_prof else 'N/A'),
            'branch': (student_prof.department.name if (student_prof and student_prof.department) else getattr(student_prof, 'branch', 'N/A')) if student_prof else 'N/A',
            'status': (self.attendance_status or 'PRESENT').upper(),
            'markedById': self.marked_by_id,
            'markedByName': marked_by_name,
            'markedAt': self.marked_at.isoformat() if self.marked_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class EventPrize(db.Model):
    __tablename__ = 'event_prizes'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
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
    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uq_event_organizer'),
        db.Index('ix_event_organizer_lookup', 'event_id', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    organizer_role = db.Column(db.String(50), nullable=False, default='ORGANIZER')
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', lazy=True)

    def to_dict(self):
        sp = self.user.student_profile if (self.user and hasattr(self.user, 'student_profile')) else None
        fp = self.user.faculty_profile if (self.user and hasattr(self.user, 'faculty_profile')) else None
        u_name = sp.full_name if sp else (fp.full_name if fp else (self.user.email if self.user else None))
        reg_id = (sp.registration_id or sp.roll_no) if sp else (fp.employee_id if fp else None)
        u_status = self.user.account_status if self.user else 'ACTIVE'

        return {
            'id': self.id,
            'eventId': self.event_id,
            'userId': self.user_id,
            'userName': u_name,
            'registerNumber': reg_id,
            'rollNumber': reg_id,
            'userStatus': u_status,
            'isLegacy': (u_status == 'LEGACY'),
            'role': self.organizer_role,
            'assignedAt': self.assigned_at.isoformat() if self.assigned_at else None,
        }


class EventVolunteerPosition(db.Model):
    __tablename__ = 'event_volunteer_positions'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    position_name = db.Column(db.String(100), nullable=False, index=True)
    max_capacity = db.Column(db.Integer, nullable=False, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship('Event', backref=db.backref('volunteer_positions', lazy=True, cascade='all, delete-orphan'))

    __table_args__ = (db.UniqueConstraint('event_id', 'position_name', name='uq_event_pos_name'),)

    def to_dict(self):
        vols = EventVolunteer.query.filter_by(
            event_id=self.event_id,
            position_name=self.position_name
        ).all()
        active_vols = [v for v in vols if v.computed_status in ['APPROVED', 'ACTIVE']]
        filled_count = len(active_vols)
        is_full = filled_count >= self.max_capacity

        return {
            'id': self.id,
            'eventId': self.event_id,
            'positionName': self.position_name,
            'name': self.position_name,
            'maxCapacity': self.max_capacity,
            'capacity': self.max_capacity,
            'filledCount': filled_count,
            'isFull': is_full,
            'status': 'FULL' if is_full else 'AVAILABLE'
        }


class EventVolunteer(db.Model):
    __tablename__ = 'event_volunteers'
    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', 'position_name', name='uq_event_volunteer_user_pos'),
        db.Index('ix_event_volunteer_lookup', 'event_id', 'user_id', 'volunteer_status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'), nullable=True, index=True)
    position_name = db.Column(db.String(100), nullable=False, default='General Volunteer', index=True)
    volunteer_status = db.Column(db.String(30), nullable=False, default='PENDING', index=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', lazy=True)
    request_ticket = db.relationship('Request', lazy=True, foreign_keys=[request_id])

    @property
    def computed_status(self):
        status_upper = (self.volunteer_status or 'PENDING').upper()
        if status_upper in ['APPROVED', 'ACTIVE']:
            if self.end_date:
                now = datetime.utcnow()
                if now > self.end_date:
                    return 'EXPIRED'
            return 'ACTIVE'
        return status_upper

    def check_expiry(self):
        if self.volunteer_status in ['APPROVED', 'ACTIVE'] and self.end_date:
            if datetime.utcnow() > self.end_date:
                self.volunteer_status = 'EXPIRED'
                db.session.commit()

    def to_dict(self):
        sp = self.user.student_profile if (self.user and hasattr(self.user, 'student_profile')) else None
        fp = self.user.faculty_profile if (self.user and hasattr(self.user, 'faculty_profile')) else None
        u_name = sp.full_name if sp else (fp.full_name if fp else (self.user.email if self.user else None))
        reg_id = (sp.registration_id or sp.roll_no) if sp else (fp.employee_id if fp else None)
        u_status = self.user.account_status if self.user else 'ACTIVE'
        c_name = self.event.club.club_name if (self.event and self.event.club) else 'Campus Club'

        return {
            'id': self.id,
            'eventId': self.event_id,
            'eventName': self.event.event_name if self.event else None,
            'clubName': c_name,
            'userId': self.user_id,
            'userName': u_name,
            'registerNumber': reg_id,
            'rollNumber': reg_id,
            'userStatus': u_status,
            'isLegacy': (u_status == 'LEGACY'),
            'positionName': self.position_name,
            'position': self.position_name,
            'requestId': self.request_id,
            'status': self.computed_status,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'requestedAt': self.requested_at.isoformat() if self.requested_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
