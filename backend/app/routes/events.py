from datetime import datetime, time
from flask import Blueprint, request, jsonify, g, Response
from app.models import db
from app.models.club import Club, ClubOrganizer, ClubFaculty
from app.models.events import (
    Event, Venue,
    EventScheduleItem, EventAnnouncement,
    EventRegistration, EventAttendance, EventSession, ParticipantRoundStatus,
    EventPrize, EventOrganizer, EventVolunteer,
)
from app.models.tickets import ActionTicket, ActionTicketType
from app.utils.auth_jwt import jwt_required, roles_required, check_legacy_user_action
from app.services.event_service import EventService
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.notification import Notification
from app.models.tickets import AssignmentTicket, AssignmentStatus, AssignmentRole
from app.services.event_service import EventService

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

    # 1. Admin always has global management rights
    if role_name == 'ADMIN':
        return True

    # 2. For Club Events:
    if event.club_id:
        if role_name == 'FACULTY':
            from app.models.club import ClubFaculty
            if ClubFaculty.query.filter_by(faculty_id=user.id, club_id=event.club_id).first() is not None:
                return True
            if event.created_by == user.id:
                return True
            return False

        if event.created_by == user.id:
            return True

        if EventOrganizer.query.filter_by(event_id=event.id, user_id=user.id).first():
            return True

        if ClubOrganizer.query.filter_by(club_id=event.club_id, user_id=user.id).first():
            return True

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

        return False

    # 3. For General Events (event.club_id is None):
    # Only assigned Faculty / Creator or Admin can manage
    if event.created_by == user.id:
        return True

    if EventOrganizer.query.filter_by(event_id=event.id, user_id=user.id).first():
        return True

    return False

def _can_take_attendance(event, user):
    if not user or user.account_status != 'ACTIVE':
        return False

    # 1. Admin, Faculty Coordinator of that club, or Organizer of that event/club
    if _can_manage_event(event, user):
        return True

    # 2. Approved Volunteer for this specific event / club
    vol = EventVolunteer.query.filter_by(event_id=event.id, user_id=user.id, volunteer_status='APPROVED').first()
    if vol:
        return True

    if event.club_id:
        from app.models.club import ClubMembership
        mem = ClubMembership.query.filter_by(
            club_id=event.club_id,
            user_id=user.id,
            membership_role='VOLUNTEER',
            membership_status='ACTIVE'
        ).first()
        if mem:
            return True

    return False


def _auto_create_sessions(event):
    """Auto-create attendance sessions for an event that has none.

    Rules:
    - COMPETITION / HACKATHON: create initial 'Round 1 — Preliminary' session.
    - Simple non-competition 1-day events: create a single session named after the event date (e.g. 20 Aug 2026).
    - Multi-day non-competition events: create one session per calendar day (capped at 31).
    """
    from datetime import timedelta

    start = event.start_date
    if not start:
        return []

    end = event.end_date or start
    start_time_str = event.start_time.strftime('%H:%M:%S') if event.start_time else '09:00:00'
    end_time_str   = event.end_time.strftime('%H:%M:%S')   if event.end_time   else '17:00:00'

    event_fmt = (event.event_format or 'COMPETITION').upper()
    num_days = (end - start).days + 1 if end and start else 1

    sessions_to_create = []

    if event_fmt in ('COMPETITION', 'HACKATHON'):
        # Initial round session for competitions
        sessions_to_create.append(EventSession(
            event_id=event.id,
            name='Round 1 — Preliminary',
            round_number=1,
            status='ACTIVE',
            session_date=start,
            start_time=start_time_str,
            end_time=end_time_str,
            description='Auto-created round attendance session'
        ))
    elif num_days == 1:
        # Date-based session for non-competition single-day event
        day_label = start.strftime('%d %b %Y')
        sessions_to_create.append(EventSession(
            event_id=event.id,
            name=day_label,
            round_number=1,
            status='UPCOMING' if start > datetime.utcnow().date() else 'ACTIVE',
            session_date=start,
            start_time=start_time_str,
            end_time=end_time_str,
            description=f'Attendance session for {day_label}'
        ))
    else:
        # Multi-day non-competition event: one session per calendar day
        cap = min(num_days, 31)
        for i in range(cap):
            day = start + timedelta(days=i)
            day_label = day.strftime('%d %b %Y')
            sessions_to_create.append(EventSession(
                event_id=event.id,
                name=day_label,
                round_number=i + 1,
                status='UPCOMING' if day > datetime.utcnow().date() else 'ACTIVE',
                session_date=day,
                start_time=start_time_str,
                end_time=end_time_str,
                description=f'Attendance session for {day_label}'
            ))

    for s in sessions_to_create:
        db.session.add(s)
    db.session.commit()
    return sessions_to_create


@events_bp.route('', methods=['GET'])
@jwt_required
def get_events():
    search_q = request.args.get('search')
    club_id = request.args.get('club_id')
    status = request.args.get('status')

    events = EventService.get_events(
        search_q=search_q,
        club_id=club_id,
        status=status
    )

    return jsonify(events), 200


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

    try:
        result = EventService.create_event(
            data,
            g.current_user.id
        )
        return jsonify(result), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@events_bp.route('/<int:event_id>/edit', methods=['PUT'])
@jwt_required
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    current_user = g.current_user

    if not _can_manage_event(event, current_user):
        return jsonify({
            'error': 'You do not have permission to edit this event.'
        }), 403

    data = request.get_json() or {}

    try:
        result = EventService.update_event(
            event_id,
            data
        )
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@events_bp.route('/<int:event_id>/status', methods=['PATCH'])
@jwt_required
def update_event_status(event_id):
    event = Event.query.get_or_404(event_id)

    if not _can_manage_event(event, g.current_user):
        return jsonify({
            'error': 'You do not have permission to change event status.'
        }), 403

    data = request.get_json() or {}
    status = (data.get('status') or '').strip()

    if not status:
        return jsonify({
            'error': 'status is required.'
        }), 400

    try:
        result = EventService.update_event_status(
            event_id,
            status
        )
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@events_bp.route('/<int:event_id>/venue', methods=['POST'])
@jwt_required
def assign_venue(event_id):
    event = Event.query.get_or_404(event_id)

    if not _can_manage_event(event, g.current_user):
        return jsonify({
            'error': 'You do not have permission to assign a venue.'
        }), 403

    data = request.get_json() or {}
    venue_id = data.get('venueId')

    if not venue_id:
        return jsonify({
            'error': 'venueId is required.'
        }), 400

    try:
        result = EventService.assign_venue(
            event_id,
            venue_id
        )
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@events_bp.route('/calendar', methods=['GET'])
@jwt_required
def get_calendar_events():
    calendar_items = EventService.get_calendar_events(g.current_user)
    return jsonify(calendar_items), 200


@events_bp.route('/<int:event_id>/schedule-conflicts', methods=['GET'])
@jwt_required
def get_schedule_conflicts(event_id):
    conflicts = EventService.get_schedule_conflicts(g.current_user.id, event_id)
    return jsonify({"conflicts": conflicts}), 200


@events_bp.route('/<int:event_id>/report', methods=['GET'])
@jwt_required
def download_event_report(event_id):
    event = Event.query.get_or_404(event_id)

    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to download this report.'}), 403

    pdf_bytes = EventService.generate_event_report_pdf(event_id)
    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in event.event_name).strip().replace(' ', '_')

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{safe_name or "event"}_report.pdf"'
        }
    )


@events_bp.route('/<int:event_id>/register', methods=['POST'])
@jwt_required
def register_for_event(event_id):
    legacy_err = check_legacy_user_action(g.current_user)
    if legacy_err:
        return legacy_err

    event = Event.query.get_or_404(event_id)
    existing = EventRegistration.query.filter_by(event_id=event.id, user_id=g.current_user.id).first()
    if existing:
        if existing.registration_status == 'CANCELLED':
            existing.registration_status = _resolve_registration_status(event)
            existing.registered_at = datetime.utcnow()
            db.session.commit()
            return jsonify(existing.to_dict()), 200
        return jsonify(existing.to_dict()), 200

    status = _resolve_registration_status(event)
    registration = EventRegistration(event_id=event.id, user_id=g.current_user.id, registration_status=status)
    db.session.add(registration)
    db.session.commit()

    NotificationService.notify_event_registered(
        event.id,
        event.event_name,
        event.club.club_name if event.club else None,
        g.current_user.id
    )

    if status == 'WAITLISTED':
        db.session.add(Notification(
            user_id=g.current_user.id,
            title="Added to Waitlist",
            message=f"{event.event_name} is at full capacity. You've been added to the waitlist and will be notified if a spot opens up.",
            type='EVENT_WAITLISTED',
            reference_url=f"/student/events/{event.id}",
            entity_id=event.id
        ))
        db.session.commit()

    return jsonify(registration.to_dict()), 201


def _resolve_registration_status(event):
    """Returns REGISTERED if the event still has capacity, otherwise WAITLISTED.
    An event with capacity 0 is treated as unlimited (no cap set)."""
    if not event.capacity or event.capacity <= 0:
        return 'REGISTERED'

    confirmed_count = EventRegistration.query.filter(
        EventRegistration.event_id == event.id,
        EventRegistration.registration_status == 'REGISTERED'
    ).count()

    return 'REGISTERED' if confirmed_count < event.capacity else 'WAITLISTED'


@events_bp.route('/<int:event_id>/register', methods=['DELETE'])
@jwt_required
def cancel_registration(event_id):
    event = Event.query.get_or_404(event_id)
    registration = EventRegistration.query.filter_by(
        event_id=event.id, user_id=g.current_user.id
    ).first()

    if not registration or registration.registration_status == 'CANCELLED':
        return jsonify({'error': 'You are not registered for this event.'}), 404

    was_confirmed = registration.registration_status == 'REGISTERED'
    registration.registration_status = 'CANCELLED'
    db.session.commit()

    # If a confirmed seat just opened up, promote the earliest waitlisted student
    if was_confirmed and event.capacity and event.capacity > 0:
        next_in_line = EventRegistration.query.filter_by(
            event_id=event.id, registration_status='WAITLISTED'
        ).order_by(EventRegistration.registered_at.asc()).first()

        if next_in_line:
            next_in_line.registration_status = 'REGISTERED'
            db.session.add(Notification(
                user_id=next_in_line.user_id,
                title="You're In! Spot Confirmed",
                message=f"A spot opened up for {event.event_name} and you've been moved from the waitlist to confirmed.",
                type='EVENT_PROMOTED',
                reference_url=f"/student/events/{event.id}",
                entity_id=event.id
            ))
            db.session.commit()

    return jsonify({'status': 'CANCELLED'}), 200


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
            ann = EventAnnouncement(
                event_id=event.id,
                title=item.get('title', 'Announcement'),
                message=item.get('message'),
                created_by_id=g.current_user.id
            )
            db.session.add(ann)
    else:
        if not data.get('message'):
            return jsonify({'error': 'message is required.'}), 400
        ann = EventAnnouncement(
            event_id=event.id,
            title=data.get('title', 'Announcement'),
            message=data.get('message'),
            created_by_id=g.current_user.id
        )
        db.session.add(ann)

        # Dispatch targeted notifications to registered participants
        registrations = EventRegistration.query.filter_by(event_id=event.id).all()
        for reg in registrations:
            db.session.add(Notification(
                user_id=reg.user_id,
                title=f"[{event.event_name}] {data.get('title', 'Announcement')}",
                message=data.get('message'),
                type='ANNOUNCEMENT',
                reference_url=f"/student/events/{event.id}",
                entity_id=event.id
            ))

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


@events_bp.route('/<int:event_id>/sessions', methods=['GET', 'POST'])
@jwt_required
def manage_event_sessions(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'GET':
        if not _can_take_attendance(event, g.current_user):
            return jsonify({'error': 'Unauthorized'}), 403

        sessions = EventSession.query.filter_by(event_id=event.id).order_by(EventSession.round_number.asc(), EventSession.id.asc()).all()
        if not sessions:
            sessions = _auto_create_sessions(event)

        return jsonify({'success': True, 'data': [s.to_dict() for s in sessions]}), 200

    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to create attendance sessions.'}), 403

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Session name is required.'}), 400

    # Handle Associated Round — inherit its round_number for participant scoping
    associated_round_id = data.get('associatedRoundId')
    round_context_label = None
    if associated_round_id:
        linked_round = EventSession.query.filter_by(id=int(associated_round_id), event_id=event.id).first()
        if linked_round:
            # New session inherits the round's participant scope via same round_number
            inherited_round_number = linked_round.round_number
            round_context_label = linked_round.name
        else:
            inherited_round_number = None
    else:
        inherited_round_number = None

    existing_count = EventSession.query.filter_by(event_id=event.id).count()
    round_number = inherited_round_number or data.get('roundNumber') or (existing_count + 1)
    status = (data.get('status') or 'UPCOMING').upper()
    session_date = _parse_date(data.get('sessionDate')) or event.start_date
    start_time = data.get('startTime') or '09:00 AM'
    end_time = data.get('endTime') or '05:00 PM'
    # Store round context label in description as JSON prefix for display
    base_desc = (data.get('description') or '').strip()
    if round_context_label:
        description = f'__linked_round__:{associated_round_id}:{round_context_label}|{base_desc}'
    else:
        description = base_desc

    new_session = EventSession(
        event_id=event.id,
        name=name,
        round_number=round_number,
        status=status,
        session_date=session_date,
        start_time=start_time,
        end_time=end_time,
        description=description
    )
    db.session.add(new_session)
    db.session.commit()

    return jsonify({'success': True, 'message': f"Session '{name}' created.", 'data': new_session.to_dict()}), 201


@events_bp.route('/<int:event_id>/sessions/<int:session_id>/status', methods=['PATCH'])
@jwt_required
def update_session_status(event_id, session_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'Unauthorized'}), 403

    session = EventSession.query.filter_by(id=session_id, event_id=event.id).first_or_404()
    data = request.get_json() or {}
    status = (data.get('status') or 'ACTIVE').upper()
    if status not in ('UPCOMING', 'ACTIVE', 'COMPLETED'):
        return jsonify({'error': 'Invalid status'}), 400

    session.status = status
    db.session.commit()
    return jsonify({'success': True, 'data': session.to_dict()}), 200


@events_bp.route('/<int:event_id>/sessions/<int:session_id>/shortlist', methods=['POST'])
@jwt_required
def shortlist_round_participants(event_id, session_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to shortlist participants for this event.'}), 403

    session = EventSession.query.filter_by(id=session_id, event_id=event.id).first_or_404()
    data = request.get_json() or {}

    selected_user_ids = set(data.get('selectedUserIds') or [])
    elimination_reason = data.get('reason') or 'Not shortlisted'

    # Determine eligible user IDs for this session/round
    if session.round_number <= 1:
        eligible_user_ids = [r.user_id for r in EventRegistration.query.filter_by(event_id=event.id).all()]
    else:
        prev_session = EventSession.query.filter_by(event_id=event.id, round_number=session.round_number - 1).first()
        if prev_session:
            eligible_user_ids = [
                prs.user_id for prs in ParticipantRoundStatus.query.filter_by(session_id=prev_session.id).filter(
                    ParticipantRoundStatus.status.in_(['SHORTLISTED', 'FINALIST', 'WINNER', 'RUNNER_UP'])
                ).all()
            ]
        else:
            eligible_user_ids = [r.user_id for r in EventRegistration.query.filter_by(event_id=event.id).all()]

    for u_id in eligible_user_ids:
        prs = ParticipantRoundStatus.query.filter_by(session_id=session.id, user_id=u_id).first()
        if not prs:
            prs = ParticipantRoundStatus(event_id=event.id, session_id=session.id, user_id=u_id)
            db.session.add(prs)

        if u_id in selected_user_ids:
            prs.status = 'SHORTLISTED'
            prs.reason = None
            total_sessions = EventSession.query.filter_by(event_id=event.id).count()
            if session.round_number == total_sessions - 1:
                NotificationService.notify_participant_finalist(event.id, event.event_name, u_id)
            else:
                NotificationService.notify_participant_shortlisted(event.id, event.event_name, u_id, session.name)
        else:
            prs.status = 'ELIMINATED'
            prs.reason = elimination_reason
            NotificationService.notify_participant_eliminated(event.id, event.event_name, u_id, session.name, elimination_reason)

        prs.updated_by_id = g.current_user.id
        prs.updated_at = datetime.utcnow()

    session.status = 'COMPLETED'
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Round '{session.name}' completed. {len(selected_user_ids)} participant(s) shortlisted to advance.",
        'data': session.to_dict()
    }), 200


@events_bp.route('/<int:event_id>/participant-progress', methods=['GET'])
@jwt_required
def get_participant_progress(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_take_attendance(event, g.current_user):
        return jsonify({'error': 'Unauthorized'}), 403

    sessions = EventSession.query.filter_by(event_id=event.id).order_by(EventSession.round_number.asc()).all()
    registrations = EventRegistration.query.filter_by(event_id=event.id).all()

    progress_list = []
    for reg in registrations:
        u = reg.user
        if not u:
            continue
        sp = getattr(u, 'student_profile', None)
        fp = getattr(u, 'faculty_profile', None)
        u_name = sp.full_name if sp else (fp.full_name if fp else u.username)
        reg_num = sp.roll_no if sp else (fp.employee_id if fp else 'N/A')
        branch = (sp.department.name if (sp and sp.department) else getattr(sp, 'branch', 'N/A')) if sp else 'N/A'

        rounds_history = []
        overall_status = 'REGISTERED'

        for s in sessions:
            att = EventAttendance.query.filter_by(session_id=s.id, user_id=u.id).first()
            prs = ParticipantRoundStatus.query.filter_by(session_id=s.id, user_id=u.id).first()

            att_status = att.attendance_status.upper() if att else 'NOT MARKED'
            round_status = prs.status if prs else ('PENDING' if att_status == 'PRESENT' else 'ELIMINATED' if att_status == 'ABSENT' else 'REGISTERED')

            if prs and prs.status:
                overall_status = prs.status

            rounds_history.append({
                'sessionId': s.id,
                'roundName': s.name,
                'roundNumber': s.round_number,
                'attendance': att_status,
                'status': round_status,
                'reason': prs.reason if prs else None
            })

        progress_list.append({
            'userId': u.id,
            'userName': u_name,
            'userEmail': u.email,
            'registerNumber': reg_num,
            'branch': branch,
            'overallStatus': overall_status,
            'roundsHistory': rounds_history
        })

    return jsonify({'success': True, 'data': progress_list}), 200


@events_bp.route('/<int:event_id>/attendance', methods=['GET', 'POST', 'PUT'])
@jwt_required
def manage_attendance(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_take_attendance(event, g.current_user):
        return jsonify({'error': 'You do not have permission to manage attendance for this event.'}), 403

    sessions = EventSession.query.filter_by(event_id=event.id).order_by(EventSession.round_number.asc(), EventSession.id.asc()).all()
    if not sessions:
        sessions = _auto_create_sessions(event)

    today = datetime.utcnow().date()

    if request.method == 'GET':
        session_id_arg = request.args.get('sessionId')
        active_session = None
        if session_id_arg:
            active_session = EventSession.query.filter_by(id=int(session_id_arg), event_id=event.id).first()
        if not active_session:
            active_session = sessions[0]

        target_date = active_session.session_date if active_session and active_session.session_date else event.start_date
        is_available = (target_date <= today) or (g.current_user.role.name if hasattr(g.current_user.role, 'name') else str(g.current_user.role)) == 'ADMIN'

        records = EventAttendance.query.filter_by(event_id=event.id, session_id=active_session.id).all()
        att_map = {r.user_id: r for r in records}
        prs_records = ParticipantRoundStatus.query.filter_by(session_id=active_session.id).all()
        prs_map = {p.user_id: p for p in prs_records}

        # Handle Round N Eligibility Filter
        if active_session.round_number <= 1:
            registrations = EventRegistration.query.filter_by(event_id=event.id).all()
        else:
            prev_session = EventSession.query.filter_by(event_id=event.id, round_number=active_session.round_number - 1).first()
            if prev_session:
                shortlisted_uids = {
                    p.user_id for p in ParticipantRoundStatus.query.filter_by(session_id=prev_session.id).filter(
                        ParticipantRoundStatus.status.in_(['SHORTLISTED', 'FINALIST', 'WINNER', 'RUNNER_UP'])
                    ).all()
                }
                registrations = [r for r in EventRegistration.query.filter_by(event_id=event.id).all() if r.user_id in shortlisted_uids]
            else:
                registrations = EventRegistration.query.filter_by(event_id=event.id).all()

        result_participants = []
        all_sessions_count = len(sessions)
        for reg in registrations:
            r_user = reg.user
            if not r_user:
                continue
            student_prof = getattr(r_user, 'student_profile', None)
            faculty_prof = getattr(r_user, 'faculty_profile', None)
            user_name = student_prof.full_name if student_prof else (faculty_prof.full_name if faculty_prof else r_user.username)
            reg_num = student_prof.roll_no if student_prof else (faculty_prof.employee_id if faculty_prof else 'N/A')
            branch = (student_prof.department.name if (student_prof and student_prof.department) else getattr(student_prof, 'branch', 'N/A')) if student_prof else 'N/A'

            existing_record = att_map.get(r_user.id)
            existing_prs = prs_map.get(r_user.id)

            if existing_record:
                status = (existing_record.attendance_status or 'PRESENT').upper()
                mb_name = existing_record.to_dict().get('markedByName')
                updated_at = existing_record.updated_at.isoformat() if existing_record.updated_at else None
            else:
                status = 'PENDING'
                mb_name = None
                updated_at = None

            # Compute total attendance history across all sessions of this event
            user_atts = EventAttendance.query.filter_by(event_id=event.id, user_id=r_user.id).all()
            tot_present = sum(1 for a in user_atts if (a.attendance_status or '').upper() == 'PRESENT')
            tot_attendance_str = f"{tot_present} / {all_sessions_count} Present"

            result_participants.append({
                'id': existing_record.id if existing_record else None,
                'eventId': event.id,
                'sessionId': active_session.id,
                'userId': r_user.id,
                'userName': user_name,
                'userEmail': r_user.email,
                'registerNumber': reg_num,
                'branch': branch,
                'status': status,
                'totalPresent': tot_present,
                'totalSessions': all_sessions_count,
                'totalAttendance': tot_attendance_str,
                'competitionStatus': existing_prs.status if existing_prs else 'REGISTERED',
                'markedByName': mb_name,
                'updatedAt': updated_at
            })

        present_cnt = sum(1 for p in result_participants if p['status'] == 'PRESENT')
        absent_cnt = sum(1 for p in result_participants if p['status'] == 'ABSENT')
        pending_cnt = sum(1 for p in result_participants if p['status'] == 'PENDING')
        eligible_cnt = len(result_participants)
        pct = round((present_cnt / eligible_cnt) * 100) if eligible_cnt > 0 else 0

        summary = {
            'present': present_cnt,
            'absent': absent_cnt,
            'pending': pending_cnt,
            'eligible': eligible_cnt,
            'total': eligible_cnt,
            'percentage': pct
        }

        # Compute eligible count per session for the overview history
        history = []
        for s in sessions:
            s_dict = s.to_dict()
            s_present = EventAttendance.query.filter_by(event_id=event.id, session_id=s.id, attendance_status='PRESENT').count()
            s_dict['presentCount'] = s_present
            # Server-side upcoming flag
            s_target_date = s.session_date if s.session_date else event.start_date
            s_dict['isFutureDate'] = (s_target_date > today) if s_target_date else False
            # Eligible participant count for this round (respects shortlisting)
            if s.round_number <= 1:
                eligible = EventRegistration.query.filter_by(event_id=event.id).count()
            else:
                prev_s = EventSession.query.filter_by(event_id=event.id, round_number=s.round_number - 1).first()
                if prev_s:
                    eligible = ParticipantRoundStatus.query.filter_by(session_id=prev_s.id).filter(
                        ParticipantRoundStatus.status.in_(['SHORTLISTED', 'FINALIST', 'WINNER', 'RUNNER_UP'])
                    ).count()
                else:
                    eligible = EventRegistration.query.filter_by(event_id=event.id).count()
            s_dict['eligibleCount'] = eligible
            history.append(s_dict)

        total_registered = EventRegistration.query.filter_by(event_id=event.id).count()
        is_round_based = (event.event_format or 'COMPETITION').upper() in ('COMPETITION', 'HACKATHON') or len(sessions) > 1

        has_valid_dates = event.start_date is not None and len(sessions) > 0

        return jsonify({
            'success': True,
            'event': event.to_dict(),
            'session': active_session.to_dict() if active_session else None,
            'sessions': history,
            'rounds': history,
            'isRoundBased': is_round_based,
            'summary': summary,
            'isAttendanceAvailable': is_available,
            'availableFromDate': target_date.strftime('%d %b %Y') if target_date else None,
            'isFutureDate': target_date > today if target_date else False,
            'participants': result_participants,
            'hasParticipants': total_registered > 0,
            'hasValidDates': has_valid_dates,
            'eventFormat': (event.event_format or 'COMPETITION').upper(),
            'totalRegistered': total_registered
        }), 200

    data = request.get_json() or {}
    session_id = data.get('sessionId') or (sessions[0].id if sessions else None)
    if not session_id:
        return jsonify({'error': 'No session specified for attendance.'}), 400

    target_session = EventSession.query.filter_by(id=int(session_id), event_id=event.id).first()
    if not target_session:
        return jsonify({'error': 'Invalid attendance session specified for this event.'}), 400

    target_date = target_session.session_date if target_session.session_date else event.start_date
    user_role_str = str(getattr(g.current_user.role, 'name', g.current_user.role)).upper()
    if target_date and target_date > today and user_role_str != 'ADMIN':
        return jsonify({
            'error': f'Attendance unavailable: Attendance will be available on {target_date.strftime("%d %b %Y")}.'
        }), 400

    # Determine eligible user IDs for this specific session/round from DB
    if target_session.round_number <= 1:
        eligible_uids = {r.user_id for r in EventRegistration.query.filter_by(event_id=event.id).all()}
    else:
        prev_session = EventSession.query.filter_by(event_id=event.id, round_number=target_session.round_number - 1).first()
        if prev_session:
            eligible_uids = {
                p.user_id for p in ParticipantRoundStatus.query.filter_by(session_id=prev_session.id).filter(
                    ParticipantRoundStatus.status.in_(['SHORTLISTED', 'FINALIST', 'WINNER', 'RUNNER_UP'])
                ).all()
            }
        else:
            eligible_uids = {r.user_id for r in EventRegistration.query.filter_by(event_id=event.id).all()}

    items = data.get('records') if 'records' in data else (data if isinstance(data, list) else [data])

    for item in items:
        u_id = item.get('userId')
        status = (item.get('status') or 'PRESENT').upper()
        if not u_id:
            continue

        # DB Validation: Ensure user is eligible for this event/round
        if eligible_uids and int(u_id) not in eligible_uids:
            continue

        # Prevent duplicates per user and session
        rec = EventAttendance.query.filter_by(event_id=event.id, session_id=target_session.id, user_id=int(u_id)).first()
        if not rec:
            rec = EventAttendance.query.filter_by(event_id=event.id, session_id=None, user_id=int(u_id)).first()

        if rec:
            rec.session_id = target_session.id
            rec.attendance_status = status
            rec.marked_by_id = g.current_user.id
            rec.updated_at = datetime.utcnow()
        else:
            rec = EventAttendance(
                event_id=event.id,
                session_id=target_session.id,
                user_id=int(u_id),
                attendance_status=status,
                marked_by_id=g.current_user.id,
                marked_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(rec)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Attendance saved successfully.'}), 200


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


@events_bp.route('/<int:event_id>/results', methods=['POST'])
@jwt_required
def declare_event_results(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to declare results for this event.'}), 403

    data = request.get_json() or {}
    winner_id = data.get('winnerUserId')
    runner_up_id = data.get('runnerUpUserId')
    second_runner_up_id = data.get('secondRunnerUpUserId')

    sessions = EventSession.query.filter_by(event_id=event.id).order_by(EventSession.round_number.desc()).all()
    if len(sessions) > 1:
        final_session = sessions[0]
        prev_session = EventSession.query.filter_by(event_id=event.id, round_number=final_session.round_number - 1).first()
        if prev_session:
            finalist_ids = {
                p.user_id for p in ParticipantRoundStatus.query.filter_by(session_id=prev_session.id).filter(
                    ParticipantRoundStatus.status.in_(['SHORTLISTED', 'FINALIST', 'WINNER', 'RUNNER_UP'])
                ).all()
            }
        else:
            finalist_ids = {r.user_id for r in EventRegistration.query.filter_by(event_id=event.id).all()}

        for uid_check, title_check in [(winner_id, 'Winner'), (runner_up_id, 'Runner-up'), (second_runner_up_id, 'Second Runner-up')]:
            if uid_check and finalist_ids and (int(uid_check) not in finalist_ids):
                return jsonify({
                    'error': f'Validation Failed: Participant ID {uid_check} did not reach the Final round and cannot be declared {title_check}.'
                }), 400

    EventPrize.query.filter_by(event_id=event.id).delete()
    positions = []

    if winner_id:
        u_w = User.query.get(winner_id)
        name_w = u_w.student_profile.full_name if (u_w and u_w.student_profile) else (u_w.faculty_profile.full_name if (u_w and u_w.faculty_profile) else (u_w.username if u_w else 'TBA'))
        db.session.add(EventPrize(event_id=event.id, title='Winner', winner_name=name_w, description='1st Place Winner'))
        positions.append({'role': 'Winner', 'name': name_w, 'userId': winner_id})
        if sessions:
            prs = ParticipantRoundStatus.query.filter_by(session_id=sessions[0].id, user_id=winner_id).first()
            if not prs:
                prs = ParticipantRoundStatus(event_id=event.id, session_id=sessions[0].id, user_id=winner_id)
                db.session.add(prs)
            prs.status = 'WINNER'

    if runner_up_id:
        u_r = User.query.get(runner_up_id)
        name_r = u_r.student_profile.full_name if (u_r and u_r.student_profile) else (u_r.faculty_profile.full_name if (u_r and u_r.faculty_profile) else (u_r.username if u_r else 'TBA'))
        db.session.add(EventPrize(event_id=event.id, title='Runner-up', winner_name=name_r, description='2nd Place Runner-up'))
        positions.append({'role': 'Runner-up', 'name': name_r, 'userId': runner_up_id})
        if sessions:
            prs = ParticipantRoundStatus.query.filter_by(session_id=sessions[0].id, user_id=runner_up_id).first()
            if not prs:
                prs = ParticipantRoundStatus(event_id=event.id, session_id=sessions[0].id, user_id=runner_up_id)
                db.session.add(prs)
            prs.status = 'RUNNER_UP'

    if second_runner_up_id:
        u_sr = User.query.get(second_runner_up_id)
        name_sr = u_sr.student_profile.full_name if (u_sr and u_sr.student_profile) else (u_sr.faculty_profile.full_name if (u_sr and u_sr.faculty_profile) else (u_sr.username if u_sr else 'TBA'))
        db.session.add(EventPrize(event_id=event.id, title='Second Runner-up', winner_name=name_sr, description='3rd Place'))
        positions.append({'role': 'Second Runner-up', 'name': name_sr, 'userId': second_runner_up_id})
        if sessions:
            prs = ParticipantRoundStatus.query.filter_by(session_id=sessions[0].id, user_id=second_runner_up_id).first()
            if not prs:
                prs = ParticipantRoundStatus(event_id=event.id, session_id=sessions[0].id, user_id=second_runner_up_id)
                db.session.add(prs)
            prs.status = 'RUNNER_UP'

    event.event_status = 'COMPLETED'
    db.session.commit()

    if winner_id:
        NotificationService.notify_participant_winner(event.id, event.event_name, winner_id, 'Winner')
    if runner_up_id:
        NotificationService.notify_participant_winner(event.id, event.event_name, runner_up_id, 'Runner-up')
    if second_runner_up_id:
        NotificationService.notify_participant_winner(event.id, event.event_name, second_runner_up_id, 'Second Runner-up')

    return jsonify({
        'success': True,
        'message': 'Results declared successfully.',
        'prizes': [p.to_dict() for p in event.prizes],
        'positions': positions
    }), 200


@events_bp.route('/<int:event_id>/announce-winners', methods=['POST'])
@jwt_required
def announce_event_winners(event_id):
    event = Event.query.get_or_404(event_id)
    if not _can_manage_event(event, g.current_user):
        return jsonify({'error': 'You do not have permission to publish winner announcements.'}), 403

    prizes = event.prizes
    if not prizes:
        return jsonify({'error': 'No results declared yet to publish.'}), 400

    title = f"{event.event_name} — Results Announced"
    lines = [f"Congratulations to the winners of {event.event_name}!\n"]
    for p in prizes:
        lines.append(f"{p.title}:\n{p.winner_name or 'TBA'}\n")

    message = "\n".join(lines)

    announcement = EventAnnouncement(
        event_id=event.id,
        title=title,
        message=message,
        created_by_id=g.current_user.id
    )
    db.session.add(announcement)

    registrations = EventRegistration.query.filter_by(event_id=event.id).all()
    for reg in registrations:
        db.session.add(Notification(
            user_id=reg.user_id,
            title=title,
            message=f"Results for {event.event_name} have been published!",
            type='COMPETITION',
            reference_url=f"/student/events/{event.id}",
            entity_id=event.id
        ))

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Winner results announced and notifications sent to participants.',
        'data': announcement.to_dict()
    }), 200


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


@events_bp.route('/<int:event_id>/volunteer-positions', methods=['GET'])
@jwt_required
def get_volunteer_positions(event_id):
    event = Event.query.get_or_404(event_id)
    positions = EventVolunteerPosition.query.filter_by(event_id=event.id).all()
    
    if not positions:
        # Seed default positions for the event in DB
        default_pos = [
            ("Registration Desk", 3),
            ("Technical Support", 2),
            ("Stage Management", 4),
            ("Photography", 2)
        ]
        for pname, cap in default_pos:
            pos = EventVolunteerPosition(event_id=event.id, position_name=pname, max_capacity=cap)
            db.session.add(pos)
        db.session.commit()
        positions = EventVolunteerPosition.query.filter_by(event_id=event.id).all()

    return jsonify([p.to_dict() for p in positions]), 200


@events_bp.route('/<int:event_id>/volunteer-apply', methods=['POST'])
@jwt_required
def apply_as_volunteer(event_id):
    user = g.current_user
    data = request.get_json() or {}
    position_name = data.get("positionName") or data.get("position") or "Registration Desk"
    
    # 1. Student must not be LEGACY
    legacy_err = check_legacy_user_action(user)
    if legacy_err:
        return legacy_err

    event = Event.query.get_or_404(event_id)

    # 2. Student must be active member of organizing club
    if not event.club_id:
        return jsonify({'error': 'Volunteer applications are only available for club events.'}), 400

    club = Club.query.get(event.club_id)
    if not club or club.club_status != 'ACTIVE':
        return jsonify({'error': 'The organizing club is not active.'}), 400

    membership = ClubMembership.query.filter_by(club_id=event.club_id, user_id=user.id, membership_status='ACTIVE').first()
    if not membership:
        return jsonify({'error': 'Must be an active member of this club to apply as a volunteer.'}), 403

    # 3. Check position capacity
    pos = EventVolunteerPosition.query.filter_by(event_id=event.id, position_name=position_name).first()
    if not pos:
        pos = EventVolunteerPosition(event_id=event.id, position_name=position_name, max_capacity=3)
        db.session.add(pos)
        db.session.flush()

    pos_dict = pos.to_dict()
    if pos_dict['isFull']:
        return jsonify({'error': f"Position '{position_name}' is FULL ({pos_dict['filledCount']}/{pos_dict['maxCapacity']} filled)."}), 400

    # 4. Check duplicate active/pending application
    existing_vol = EventVolunteer.query.filter_by(event_id=event.id, user_id=user.id, position_name=position_name).first()
    if existing_vol and existing_vol.computed_status in ['PENDING', 'APPROVED', 'ACTIVE']:
        return jsonify({'error': f"You already have an active or pending application for '{position_name}'."}), 409

    # 5. Compute 3-day time-bound duration
    start_dt = datetime.combine(event.start_date, datetime.min.time()) if event.start_date else datetime.utcnow()
    end_dt = start_dt + timedelta(days=3)

    # 6. Route Ticket to Faculty Coordinator of that specific club
    fac_coord = ClubFaculty.query.filter_by(club_id=event.club_id).first()
    if not fac_coord:
        return jsonify({'error': 'No faculty coordinator assigned to this club to approve volunteer tickets.'}), 400

    from app.models.tickets import Request, RequestApproval, ApprovalStatus
    req_title = f"Volunteer Application - {position_name} ({event.event_name})"
    req_desc = f"Student {user.email} applied for volunteer position '{position_name}' for event '{event.event_name}' from {start_dt.strftime('%b %d')} to {end_dt.strftime('%b %d, %Y')}."
    
    req = Request(
        requester_id=user.id,
        request_type="VOLUNTEER",
        title=req_title,
        description=req_desc,
        priority="MEDIUM",
        reference_type="EVENT",
        reference_id=event.id,
        reference_name=event.event_name,
        workflow_status=ApprovalStatus.PENDING
    )
    db.session.add(req)
    db.session.flush()

    # Route specifically to Club Faculty Coordinator
    appr = RequestApproval(
        request_id=req.id,
        approver_id=fac_coord.faculty_id,
        approval_role="FACULTY_COORDINATOR",
        order=1,
        status=ApprovalStatus.PENDING
    )
    db.session.add(appr)

    vol = EventVolunteer(
        event_id=event.id,
        user_id=user.id,
        request_id=req.id,
        position_name=position_name,
        volunteer_status="PENDING",
        start_date=start_dt,
        end_date=end_dt
    )
    db.session.add(vol)
    db.session.commit()

    NotificationService.notify_request_submitted(fac_coord.faculty_id, req.id, req_title)

    return jsonify({
        'success': True,
        'message': f"Volunteer ticket for '{position_name}' submitted to Faculty Coordinator.",
        'data': vol.to_dict(),
        'ticket': req.to_dict()
    }), 201


@events_bp.route('/organizer/my-events', methods=['GET'])
@jwt_required
def get_my_managed_events():
    user = g.current_user

    events = Event.query.join(EventOrganizer).filter(
        EventOrganizer.user_id == user.id
    ).all()

    return jsonify([e.to_dict() for e in events]), 200
