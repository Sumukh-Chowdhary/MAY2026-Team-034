from datetime import datetime, time
from app.models import db
from app.models.club import Club, ClubOrganizer, ClubFaculty
from app.models.events import (
    Event, Venue,
    EventScheduleItem, EventAnnouncement,
    EventRegistration, EventAttendance,
    EventPrize, EventOrganizer, EventVolunteer,
)
from app.models.user import User
from app.extensions import socketio

def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value)).date()
    except Exception:
        return None

def _parse_time(value):
    if value is None or value == '':
        return None
    try:
        return datetime.fromisoformat(str(value)).time()
    except Exception:
        try:
            return time.fromisoformat(str(value))
        except Exception:
            return None

class EventService:
    @staticmethod
    def get_events(search_q=None, club_id=None, status=None):
        query = Event.query
        if club_id:
            query = query.filter(Event.club_id == club_id)
        if status:
            query = query.filter(Event.event_status == status.upper())

        if search_q:
            q = f"%{search_q.strip().lower()}%"
            query = query.join(Club, Event.club_id == Club.id).outerjoin(Venue, Event.venue_id == Venue.id).filter(
                db.or_(
                    db.func.lower(Event.event_name).like(q),
                    db.func.lower(Event.event_description).like(q),
                    db.func.lower(Club.club_name).like(q),
                    db.func.lower(Venue.venue_name).like(q),
                )
            )

        events = query.order_by(Event.start_date.asc()).all()
        return [event.to_dict() for event in events]

    @staticmethod
    def get_my_events(user_id, scope='registered'):
        if scope == 'participated':
            attendance = EventAttendance.query.filter_by(user_id=user_id).all()
            events = [record.event for record in attendance if record.event]
        else:
            registrations = EventRegistration.query.filter_by(user_id=user_id).filter(
                EventRegistration.registration_status != 'CANCELLED'
            ).all()
            events = [record.event for record in registrations if record.event]
        return [event.to_dict() for event in events]

    @staticmethod
    def get_event_by_id(event_id):
        event = Event.query.get_or_404(event_id)
        return event.to_dict()

    @staticmethod
    def create_event(data, creator_id):
        club_id = data.get('clubId') or data.get('club_id')
        if not club_id and data.get('club'):
            club = Club.query.filter(db.func.lower(Club.club_name) == str(data.get('club')).strip().lower()).first()
            club_id = club.id if club else None
        if not club_id and data.get('clubName'):
            club = Club.query.filter(db.func.lower(Club.club_name) == str(data.get('clubName')).strip().lower()).first()
            club_id = club.id if club else None

        name = (data.get('name') or '').strip()
        description = data.get('description')
        venue_id = data.get('venueId')
        status = (data.get('status') or 'SCHEDULED').upper()
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        capacity = data.get('capacity') or 0

        if not club_id:
            raise ValueError('clubId is required.')
        if not name:
            raise ValueError('Event name is required.')
        if not start_date or not end_date:
            raise ValueError('Event startDate and endDate are required.')

        club = Club.query.get(club_id)
        if not club:
            raise ValueError('Club not found.')

        venue = None
        if venue_id:
            venue = Venue.query.get(venue_id)
            if not venue:
                raise ValueError('Venue not found.')

        parsed_start_date = _parse_date(start_date)
        parsed_end_date = _parse_date(end_date)
        if not parsed_start_date or not parsed_end_date:
            raise ValueError('startDate and endDate must be ISO format YYYY-MM-DD.')

        event = Event(
            club_id=club.id,
            venue_id=venue.id if venue else None,
            created_by=creator_id,
            event_name=name,
            event_description=description,
            event_status=status,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            start_time=_parse_time(start_time),
            end_time=_parse_time(end_time),
            capacity=capacity,
        )
        db.session.add(event)
        db.session.commit()

        socketio.emit('event_created', event.to_dict(), room='events_room')
        return event.to_dict()

    @staticmethod
    def update_event(event_id, data):
        event = Event.query.get_or_404(event_id)
        if data.get('name') is not None:
            event.event_name = data.get('name').strip()
        if data.get('description') is not None:
            event.event_description = data.get('description')
        if data.get('venueId') is not None:
            venue = Venue.query.get(data.get('venueId'))
            if not venue:
                raise ValueError('Venue not found.')
            event.venue_id = venue.id
        if data.get('status') is not None:
            event.event_status = data.get('status').upper()
        if data.get('startDate') is not None:
            parsed = _parse_date(data.get('startDate'))
            if not parsed:
                raise ValueError('startDate must be YYYY-MM-DD.')
            event.start_date = parsed
        if data.get('endDate') is not None:
            parsed = _parse_date(data.get('endDate'))
            if not parsed:
                raise ValueError('endDate must be YYYY-MM-DD.')
            event.end_date = parsed
        if data.get('startTime') is not None:
            event.start_time = _parse_time(data.get('startTime'))
        if data.get('endTime') is not None:
            event.end_time = _parse_time(data.get('endTime'))
        if data.get('capacity') is not None:
            event.capacity = data.get('capacity')

        db.session.commit()
        dict_data = event.to_dict()
        socketio.emit('event_updated', dict_data, room=f'event_{event.id}')
        socketio.emit('event_updated', dict_data, room='events_room')
        return dict_data

    @staticmethod
    def update_event_status(event_id, status):
        event = Event.query.get_or_404(event_id)
        event.event_status = status.upper()
        db.session.commit()
        dict_data = event.to_dict()
        socketio.emit('event_updated', dict_data, room=f'event_{event.id}')
        socketio.emit('event_updated', dict_data, room='events_room')
        return dict_data

    @staticmethod
    def assign_venue(event_id, venue_id):
        event = Event.query.get_or_404(event_id)
        venue = Venue.query.get(venue_id)
        if not venue:
            raise ValueError('Venue not found.')
        event.venue_id = venue.id
        db.session.commit()
        dict_data = event.to_dict()
        socketio.emit('event_updated', dict_data, room=f'event_{event.id}')
        socketio.emit('event_updated', dict_data, room='events_room')
        return dict_data

    @staticmethod
    def register_for_event(event_id, user_id):
        event = Event.query.get_or_404(event_id)
        existing = EventRegistration.query.filter_by(event_id=event.id, user_id=user_id).first()
        if existing:
            return existing.to_dict()
        registration = EventRegistration(event_id=event.id, user_id=user_id)
        db.session.add(registration)
        db.session.commit()

        dict_data = registration.to_dict()
        socketio.emit('registration_added', dict_data, room=f'event_{event.id}')
        return dict_data

    @staticmethod
    def manage_schedule(event_id, data, replace=False):
        event = Event.query.get_or_404(event_id)
        if replace:
            EventScheduleItem.query.filter_by(event_id=event.id).delete()
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not item.get('activity'):
                    continue
                db.session.add(EventScheduleItem(event_id=event.id, schedule_time=item.get('time', ''), activity=item.get('activity')))
        else:
            if not data.get('activity'):
                raise ValueError('activity is required.')
            db.session.add(EventScheduleItem(event_id=event.id, schedule_time=data.get('time', ''), activity=data.get('activity')))

        db.session.commit()
        dict_data = event.to_dict()
        socketio.emit('event_schedule_updated', {'eventId': event.id, 'schedule': dict_data['schedule']}, room=f'event_{event.id}')
        return dict_data

    @staticmethod
    def manage_announcements(event_id, data, replace=False):
        event = Event.query.get_or_404(event_id)
        if replace:
            EventAnnouncement.query.filter_by(event_id=event.id).delete()
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not item.get('message'):
                    continue
                db.session.add(EventAnnouncement(event_id=event.id, title=item.get('title', 'Announcement'), message=item.get('message')))
        else:
            if not data.get('message'):
                raise ValueError('message is required.')
            db.session.add(EventAnnouncement(event_id=event.id, title=data.get('title', 'Announcement'), message=data.get('message')))

        db.session.commit()
        dict_data = event.to_dict()
        socketio.emit('event_announcement_created', {'eventId': event.id, 'announcements': dict_data['announcements']}, room=f'event_{event.id}')
        return dict_data

    @staticmethod
    def manage_attendance(event_id, data, replace=False):
        event = Event.query.get_or_404(event_id)
        if replace:
            items = data if isinstance(data, list) else [data]
            EventAttendance.query.filter_by(event_id=event.id).delete()
            for item in items:
                user_id = item.get('userId')
                if not user_id:
                    continue
                db.session.add(EventAttendance(event_id=event.id, user_id=user_id, attendance_status=(item.get('status') or 'PRESENT').upper()))
        else:
            user_id = data.get('userId')
            if not user_id:
                raise ValueError('userId is required.')
            record = EventAttendance.query.filter_by(event_id=event.id, user_id=user_id).first()
            if record:
                record.attendance_status = (data.get('status') or record.attendance_status).upper()
            else:
                db.session.add(EventAttendance(event_id=event.id, user_id=user_id, attendance_status=(data.get('status') or 'PRESENT').upper()))

        db.session.commit()
        dict_data = event.to_dict()
        socketio.emit('event_attendance_updated', {'eventId': event.id, 'attendance': dict_data['attendance']}, room=f'event_{event.id}')
        return dict_data

    @staticmethod
    def manage_prizes(event_id, data, replace=False):
        event = Event.query.get_or_404(event_id)
        if replace:
            EventPrize.query.filter_by(event_id=event.id).delete()
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not item.get('title'):
                    continue
                db.session.add(EventPrize(event_id=event.id, title=item.get('title'), winner_name=item.get('winnerName'), description=item.get('description')))
        else:
            if not data.get('title'):
                raise ValueError('title is required.')
            db.session.add(EventPrize(event_id=event.id, title=data.get('title'), winner_name=data.get('winnerName'), description=data.get('description')))

        db.session.commit()
        dict_data = event.to_dict()
        socketio.emit('event_prize_updated', {'eventId': event.id, 'prizes': dict_data['prizes']}, room=f'event_{event.id}')
        return dict_data

    @staticmethod
    def manage_volunteers(event_id, user_id, status='PENDING', is_management=False):
        event = Event.query.get_or_404(event_id)
        volunteer = EventVolunteer.query.filter_by(event_id=event.id, user_id=user_id).first()
        if volunteer:
            if is_management:
                volunteer.volunteer_status = status.upper()
            else:
                volunteer.volunteer_status = 'PENDING'
        else:
            volunteer = EventVolunteer(event_id=event.id, user_id=user_id, volunteer_status=status.upper() if is_management else 'PENDING')
            db.session.add(volunteer)

        db.session.commit()
        dict_data = volunteer.to_dict()
        socketio.emit('event_volunteer_updated', {'eventId': event.id, 'volunteer': dict_data}, room=f'event_{event.id}')
        return dict_data

    @staticmethod
    def get_calendar_events(current_user):
        events = Event.query.order_by(Event.start_date.asc()).all()
        calendar_items = []

        for event in events:
            registration = EventRegistration.query.filter_by(event_id=event.id, user_id=current_user.id).first() if current_user else None
            attendance = EventAttendance.query.filter_by(event_id=event.id, user_id=current_user.id).first() if current_user else None

            if attendance:
                reg_status = 'ATTENDED' if attendance.attendance_status.upper() == 'PRESENT' else attendance.attendance_status.upper()
            elif registration:
                reg_status = registration.registration_status.upper()
            else:
                reg_status = 'NOT_REGISTERED'

            # Color coding: Green = Registered/Attended, Blue = Open, Gray = Passed, Red = Cancelled
            if event.computed_status.upper() == 'COMPLETED':
                color = '#6b7280' # Gray for past
            elif event.event_status.upper() == 'CANCELLED':
                color = '#ef4444' # Red
            elif reg_status in {'REGISTERED', 'CONFIRMED', 'ATTENDED', 'PRESENT'}:
                color = '#10b981' # Green for registered
            else:
                color = '#3b82f6' # Blue for non-registered open event

            # Resolve Point of Contact (POC) - Faculty Coordinator or Club Organizer
            club_organizer = ClubOrganizer.query.filter_by(club_id=event.club_id).first() if event.club_id else None
            club_faculty = ClubFaculty.query.filter_by(club_id=event.club_id).first() if event.club_id else None
            contact_name = None
            contact_role = None
            contact_email = None

            if club_faculty and club_faculty.faculty:
                fac = club_faculty.faculty
                contact_name = fac.faculty_profile.full_name if fac.faculty_profile else fac.email
                contact_role = club_faculty.faculty_role or 'Faculty Coordinator'
                contact_email = fac.email
            elif club_organizer and club_organizer.user:
                org = club_organizer.user
                contact_name = org.student_profile.full_name if org.student_profile else (org.faculty_profile.full_name if org.faculty_profile else org.email)
                contact_role = club_organizer.organizer_role or 'Club Organizer'
                contact_email = org.email

            calendar_items.append({
                'id': event.id,
                'title': event.event_name,
                'name': event.event_name,
                'description': event.event_description or 'No description provided.',
                'status': event.computed_status.upper(),
                'rawStatus': event.event_status,
                'clubId': event.club_id,
                'clubName': event.club.club_name if event.club else 'General / Institutional',
                'venueId': event.venue_id,
                'venueName': event.venue.venue_name if event.venue else 'TBD',
                'venueLocation': event.venue.venue_location if event.venue else 'Campus',
                'contactName': contact_name or 'Event Admin',
                'contactRole': contact_role or 'Coordinator',
                'contactEmail': contact_email or '',
                'startDate': event.start_date.isoformat() if event.start_date else None,
                'endDate': event.end_date.isoformat() if event.end_date else None,
                'startTime': event.start_time.strftime('%H:%M') if event.start_time else '09:00',
                'endTime': event.end_time.strftime('%H:%M') if event.end_time else '17:00',
                'registrationStatus': reg_status,
                'color': color,
            })

        return calendar_items
