from datetime import datetime, time
from flask import Blueprint, request, jsonify, g
from app.models import db
from app.models.club import Club, ClubOrganizer, ClubFaculty
from app.models.events import (
    Event, Venue,
    EventScheduleItem, EventAnnouncement,
    EventRegistration, EventAttendance,
    EventPrize, EventOrganizer, EventVolunteer,
)
from app.models.tickets import ActionTicket, ActionTicketType
from app.utils.auth_jwt import jwt_required, roles_required
from app.services.event_service import EventService
from app.models.club import ClubOrganizer
from app.models.tickets import AssignmentTicket, AssignmentStatus, AssignmentRole

events_bp = Blueprint('events', __name__, url_prefix='/api/events')


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except Exception:
        return None


def _parse_time(value):
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value).time()
    except Exception:
        try:
            return time.fromisoformat(value)
        except Exception:
            return None


def _can_manage_event(event, user):
    if not user or user.account_status != 'ACTIVE':
        return False

    role_name = user.role.name.upper() if user.role else ''

    # 1. Admin & Faculty always have management rights
    if role_name in ['ADMIN', 'FACULTY']:
        if role_name == 'FACULTY' and event.club_id:
            from app.models.club import ClubFaculty
            if ClubFaculty.query.filter_by(faculty_id=user.id, club_id=event.club_id).first() is not None:
                return True
            if event.created_by == user.id:
                return True
        else:
            return True

    # 2. Check Event Creator
    if event.created_by == user.id:
        return True

    # 3. Check Event Organizer assignment
    if EventOrganizer.query.filter_by(event_id=event.id, user_id=user.id).first():
        return True

    # 4. Check Club Organizer assignment (Module 21)
    if event.club_id and ClubOrganizer.query.filter_by(club_id=event.club_id, user_id=user.id).first():
        return True

    # 5. Check Active Assignment Tickets for Club (Module 21)
    if event.club_id:
        active_assignment = AssignmentTicket.query.filter_by(
            holder_id=user.id,
            reference_type='CLUB',
            reference_id=event.club_id,
            status=AssignmentStatus.ACTIVE
        ).filter(
            AssignmentTicket.assignment_role.in_([AssignmentRole.ORGANIZER, 'PRESIDENT'])
        ).first()

        if active_assignment:
            return True

    # 6. Check Approved Event Volunteer access (Module 22)
    vol = EventVolunteer.query.filter_by(event_id=event.id, user_id=user.id, volunteer_status='APPROVED').first()
    if vol:
        return True

    return False


@events_bp.route('', methods=['GET'])
@jwt_required
def get_events():
    search_q = request.args.get('search')
    club_id = request.args.get('clubId')
    status = request.args.get('status')

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
    return jsonify([event.to_dict() for event in events]), 200


@events_bp.route('/me', methods=['GET'])
@jwt_required
def get_my_events():
    scope = (request.args.get('scope') or 'registered').lower()
    current_user = g.current_user

    if scope == 'participated':
        attendance = EventAttendance.query.filter_by(user_id=current_user.id).all()
        events = [record.event for record in attendance if record.event]
    else:
        registrations = EventRegistration.query.filter_by(user_id=current_user.id).filter(
            EventRegistration.registration_status != 'CANCELLED'
        ).all()
        events = [record.event for record in registrations if record.event]

    return jsonify([event.to_dict() for event in events]), 200


@events_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict()), 200


@events_bp.route('/create', methods=['POST'])
@jwt_required
@roles_required('ADMIN', 'FACULTY')
def create_event():
    data = request.get_json() or {}
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
        return jsonify({'error': 'clubId is required.'}), 400
    if not name:
        return jsonify({'error': 'Event name is required.'}), 400
    if not start_date or not end_date:
        return jsonify({'error': 'Event startDate and endDate are required.'}), 400

    club = Club.query.get(club_id)
    if not club:
        return jsonify({'error': 'Club not found.'}), 404

    venue = None
    if venue_id:
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({'error': 'Venue not found.'}), 404

    parsed_start_date = _parse_date(start_date)
    parsed_end_date = _parse_date(end_date)
    if not parsed_start_date or not parsed_end_date:
        return jsonify({'error': 'startDate and endDate must be ISO format YYYY-MM-DD.'}), 400

    parsed_start_time = _parse_time(start_time)
    parsed_end_time = _parse_time(end_time)

    event = Event(
        club_id=club.id,
        venue_id=venue.id if venue else None,
        created_by=g.current_user.id,
        event_name=name,
        event_description=description,
        event_status=status,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        start_time=parsed_start_time,
        end_time=parsed_end_time,
        capacity=capacity,
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@events_bp.route('/<int:event_id>/edit', methods=['PUT'])
@jwt_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    current_user = g.current_user
    if not _can_manage_event(event, current_user):
        return jsonify({'error': 'You do not have permission to edit this event.'}), 403

    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')
    venue_id = data.get('venueId')
    status = data.get('status')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    start_time = data.get('startTime')
    end_time = data.get('endTime')
    capacity = data.get('capacity')

    if name is not None:
        event.event_name = name.strip()
    if description is not None:
        event.event_description = description
    if venue_id is not None:
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({'error': 'Venue not found.'}), 404
        event.venue_id = venue.id
    if status is not None:
        event.event_status = status.upper()
    if start_date is not None:
        parsed = _parse_date(start_date)
        if not parsed:
            return jsonify({'error': 'startDate must be ISO format YYYY-MM-DD.'}), 400
        event.start_date = parsed
    if end_date is not None:
        parsed = _parse_date(end_date)
        if not parsed:
            return jsonify({'error': 'endDate must be ISO format YYYY-MM-DD.'}), 400
        event.end_date = parsed
    if start_time is not None:
        parsed = _parse_time(start_time)
        if parsed is None:
            return jsonify({'error': 'startTime must be ISO format HH:MM or HH:MM:SS.'}), 400
        event.start_time = parsed
    if end_time is not None:
        parsed = _parse_time(end_time)
        if parsed is None:
            return jsonify({'error': 'endTime must be ISO format HH:MM or HH:MM:SS.'}), 400
        event.end_time = parsed
    if capacity is not None:
        event.capacity = capacity

    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/status', methods=['PATCH'])
@jwt_required
def update_event_status(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to change event status.'}), 403

    data = request.get_json() or {}
    status = (data.get('status') or '').strip()
    if not status:
        return jsonify({'error': 'status is required.'}), 400

    event.event_status = status.upper()
    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/venue', methods=['POST'])
@jwt_required
def assign_venue(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to assign a venue.'}), 403

    data = request.get_json() or {}
    venue_id = data.get('venueId')
    if not venue_id:
        return jsonify({'error': 'venueId is required.'}), 400

    venue = Venue.query.get(venue_id)
    if not venue:
        return jsonify({'error': 'Venue not found.'}), 404

    event.venue_id = venue.id
    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/calendar', methods=['GET'])
@jwt_required
def get_calendar_events():
    calendar_items = EventService.get_calendar_events(g.current_user)
    return jsonify(calendar_items), 200


@events_bp.route('/<int:event_id>/register', methods=['POST'])
@jwt_required
def register_for_event(event_id):
    event = Event.query.get_or_404(event_id)
    existing = EventRegistration.query.filter_by(event_id=event.id, user_id=g.current_user.id).first()
    if existing:
        return jsonify(existing.to_dict()), 200

    registration = EventRegistration(event_id=event.id, user_id=g.current_user.id)
    db.session.add(registration)
    db.session.commit()
    return jsonify(registration.to_dict()), 201


@events_bp.route('/<int:event_id>/registrations', methods=['GET'])
@jwt_required
def get_registrations(event_id):
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event.id).all()
    return jsonify([item.to_dict() for item in registrations]), 200


@events_bp.route('/<int:event_id>/schedule', methods=['GET', 'POST', 'PUT'])
@jwt_required
def manage_schedule(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'GET':
        return jsonify([item.to_dict() for item in event.schedules]), 200

    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to manage schedule.'}), 403

    data = request.get_json() or {}
    if request.method == 'PUT':
        EventScheduleItem.query.filter_by(event_id=event.id).delete()
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not item.get('activity'):
                continue
            db.session.add(EventScheduleItem(event_id=event.id, schedule_time=item.get('time', ''), activity=item.get('activity')))
    else:
        if not data.get('activity'):
            return jsonify({'error': 'activity is required.'}), 400
        db.session.add(EventScheduleItem(event_id=event.id, schedule_time=data.get('time', ''), activity=data.get('activity')))

    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/announcements', methods=['GET', 'POST', 'PUT'])
@jwt_required
def manage_announcements(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'GET':
        return jsonify([item.to_dict() for item in event.announcements]), 200

    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to manage announcements.'}), 403

    data = request.get_json() or {}
    if request.method == 'PUT':
        EventAnnouncement.query.filter_by(event_id=event.id).delete()
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not item.get('message'):
                continue
            db.session.add(EventAnnouncement(event_id=event.id, title=item.get('title', 'Announcement'), message=item.get('message')))
    else:
        if not data.get('message'):
            return jsonify({'error': 'message is required.'}), 400
        db.session.add(EventAnnouncement(event_id=event.id, title=data.get('title', 'Announcement'), message=data.get('message')))

    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/tickets', methods=['POST'])
@jwt_required
def create_event_ticket(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json() or {}

    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    target_role = (data.get('targetRole') or 'ORGANIZER').upper() # 'ORGANIZER' or 'COORDINATOR'

    if not title:
        return jsonify({'success': False, 'error': 'Title is required.'}), 400

    ticket = ActionTicket(
        raised_by_id=g.current_user.id,
        ticket_type=ActionTicketType.CREATE_EVENT_FOR_CLUB,
        title=f"[{target_role}] {title}",
        description=f"Target Recipient: {target_role}\n\n{description}",
        priority=(data.get('priority') or 'MEDIUM').upper(),
        reference_type='EVENT',
        reference_id=event.id,
        reference_name=event.event_name,
    )
    db.session.add(ticket)
    db.session.flush()

    approver_user = None
    role_label = 'CLUB_ORGANIZER'

    if target_role == 'COORDINATOR' and event.club_id:
        from app.models.tickets import resolve_club_faculty
        approver_user = resolve_club_faculty(event.club_id)
        role_label = 'CLUB_FACULTY'
    elif event.club_id:
        from app.models.tickets import resolve_club_organizer
        approver_user = resolve_club_organizer(event.club_id)
        role_label = 'CLUB_ORGANIZER'

    if not approver_user and event.creator:
        approver_user = event.creator
        role_label = 'EVENT_ORGANIZER'

    if approver_user:
        ticket.add_approval_step(approver_id=approver_user.id, approval_role=role_label, order=1)
        from app.services.notification_service import NotificationService
        NotificationService.create(
            user_id=approver_user.id,
            title="New Student Event Query",
            message=f"Student ticket raised for '{event.event_name}': {title}",
            notification_type="TICKET",
            entity_id=ticket.id,
            reference_url="/notifications"
        )
    else:
        from app.models.tickets import resolve_admin
        admin = resolve_admin()
        if admin:
            ticket.add_approval_step(approver_id=admin.id, approval_role='ADMIN', order=1)

    db.session.commit()
    return jsonify({'success': True, 'message': f'Ticket raised successfully to {target_role.title()}.', 'data': ticket.to_dict()}), 201


@events_bp.route('/<int:event_id>/attendance', methods=['GET', 'POST', 'PUT'])
@jwt_required
def manage_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to manage attendance.'}), 403

    if request.method == 'GET':
        records = EventAttendance.query.filter_by(event_id=event.id).all()
        return jsonify([item.to_dict() for item in records]), 200

    data = request.get_json() or {}
    if request.method == 'PUT':
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
            return jsonify({'error': 'userId is required.'}), 400
        record = EventAttendance.query.filter_by(event_id=event.id, user_id=user_id).first()
        if record:
            record.attendance_status = (data.get('status') or record.attendance_status).upper()
        else:
            db.session.add(EventAttendance(event_id=event.id, user_id=user_id, attendance_status=(data.get('status') or 'PRESENT').upper()))

    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/prizes', methods=['GET', 'POST', 'PUT'])
@jwt_required
def manage_prizes(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to manage prizes.'}), 403

    if request.method == 'GET':
        return jsonify([item.to_dict() for item in event.prizes]), 200

    data = request.get_json() or {}
    if request.method == 'PUT':
        EventPrize.query.filter_by(event_id=event.id).delete()
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not item.get('title'):
                continue
            db.session.add(EventPrize(event_id=event.id, title=item.get('title'), winner_name=item.get('winnerName'), description=item.get('description')))
    else:
        if not data.get('title'):
            return jsonify({'error': 'title is required.'}), 400
        db.session.add(EventPrize(event_id=event.id, title=data.get('title'), winner_name=data.get('winnerName'), description=data.get('description')))

    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/organizers', methods=['GET', 'POST'])
@jwt_required
def manage_organizers(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to manage organizers.'}), 403

    if request.method == 'GET':
        return jsonify([item.to_dict() for item in event.organizers]), 200

    data = request.get_json() or {}
    user_id = data.get('userId')
    if not user_id:
        return jsonify({'error': 'userId is required.'}), 400

    organizer = EventOrganizer.query.filter_by(event_id=event.id, user_id=user_id).first()
    if organizer:
        organizer.organizer_role = (data.get('role') or organizer.organizer_role).upper()
    else:
        organizer = EventOrganizer(event_id=event.id, user_id=user_id, organizer_role=(data.get('role') or 'ORGANIZER').upper())
        db.session.add(organizer)

    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/volunteers', methods=['GET', 'POST'])
@jwt_required
def manage_volunteers(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'GET':
        return jsonify([item.to_dict() for item in event.volunteers]), 200

    data = request.get_json() or {}
    user_id = data.get('userId') or g.current_user.id
    volunteer = EventVolunteer.query.filter_by(event_id=event.id, user_id=user_id).first()
    if volunteer:
        if _can_manage_event(event, g.current_user):
            volunteer.volunteer_status = (data.get('status') or volunteer.volunteer_status).upper()
        else:
            volunteer.volunteer_status = 'PENDING'
    else:
        volunteer = EventVolunteer(event_id=event.id, user_id=user_id, volunteer_status='PENDING')
        db.session.add(volunteer)

    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/volunteers/<int:volunteer_id>', methods=['PATCH'])
@jwt_required
def update_volunteer_status(event_id, volunteer_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to manage volunteers.'}), 403

    volunteer = EventVolunteer.query.get_or_404(volunteer_id)
    if volunteer.event_id != event.id:
        return jsonify({'error': 'Volunteer not found for this event.'}), 404

    data = request.get_json() or {}
    volunteer.volunteer_status = (data.get('status') or 'PENDING').upper()
    db.session.commit()
    return jsonify(volunteer.to_dict()), 200





@events_bp.route('/organizer/my-events', methods=['GET'])
@jwt_required
def get_my_managed_events():
    user = g.current_user

    events = Event.query.join(EventOrganizer).filter(
        EventOrganizer.user_id == user.id
    ).all()

    return jsonify([e.to_dict() for e in events]), 200
