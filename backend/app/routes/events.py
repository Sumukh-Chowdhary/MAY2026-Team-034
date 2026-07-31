from datetime import datetime, time
from flask import Blueprint, request, jsonify, g
from app.models import db
from app.models.club import Club
from app.models.events import Event, Venue
from app.utils.auth_jwt import jwt_required, roles_required
from app.models.event_details import (
    EventSchedule,
    Announcement,
    EventRegistration,
    Attendance,
)


events_bp = Blueprint('events', __name__, url_prefix='/api/events')


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
                db.func.lower(Venue.venue_name).like(q)
            )
        )

    events = query.order_by(Event.start_date.asc()).all()
    return jsonify([event.to_dict() for event in events]), 200


@events_bp.route('/<int:event_id>', methods=['GET'])
@jwt_required
def get_event(event_id):
    event = Event.query.get_or_404(event_id)

    event_data = event.to_dict()

    event_data["schedule"] = [
        item.to_dict() for item in event.schedules
    ]

    event_data["announcements"] = [
        item.to_dict() for item in event.announcements
    ]

    event_data["registrations"] = [
        item.to_dict() for item in event.registrations
    ]

    event_data["attendance"] = [
        item.to_dict() for item in event.attendance
    ]

    return jsonify(event_data), 200


@events_bp.route('/create', methods=['POST'])
@jwt_required
@roles_required('ADMIN', 'FACULTY')
def create_event():
    data = request.get_json() or {}
    club_id = data.get('clubId')
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

    club = Club.query.get_or_404(club_id)
    venue = None
    if venue_id:
        venue = Venue.query.get(venue_id)
        if not venue:
            return jsonify({'error': 'Venue not found.'}), 404

    try:
        parsed_start_date = datetime.fromisoformat(start_date).date()
        parsed_end_date = datetime.fromisoformat(end_date).date()
    except Exception:
        return jsonify({'error': 'startDate and endDate must be ISO format YYYY-MM-DD.'}), 400

    def parse_time(value):
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value).time()
        except Exception:
            try:
                return time.fromisoformat(value)
            except Exception:
                return None

    parsed_start_time = parse_time(start_time)
    parsed_end_time = parse_time(end_time)

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
        capacity=capacity
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@events_bp.route('/<int:event_id>/edit', methods=['PUT'])
@jwt_required
@roles_required('ADMIN', 'FACULTY')
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    current_user = g.current_user
    is_admin = current_user.role and current_user.role.name == 'ADMIN'
    if not is_admin and event.created_by != current_user.id:
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
        try:
            event.start_date = datetime.fromisoformat(start_date).date()
        except Exception:
            return jsonify({'error': 'startDate must be ISO format YYYY-MM-DD.'}), 400
    if end_date is not None:
        try:
            event.end_date = datetime.fromisoformat(end_date).date()
        except Exception:
            return jsonify({'error': 'endDate must be ISO format YYYY-MM-DD.'}), 400
    if start_time is not None:
        try:
            event.start_time = datetime.fromisoformat(start_time).time()
        except Exception:
            try:
                event.start_time = time.fromisoformat(start_time)
            except Exception:
                return jsonify({'error': 'startTime must be ISO format HH:MM or HH:MM:SS.'}), 400
    if end_time is not None:
        try:
            event.end_time = datetime.fromisoformat(end_time).time()
        except Exception:
            try:
                event.end_time = time.fromisoformat(end_time)
            except Exception:
                return jsonify({'error': 'endTime must be ISO format HH:MM or HH:MM:SS.'}), 400
    
    if capacity is not None:
        event.capacity = capacity

    db.session.commit()
    return jsonify(event.to_dict()), 200


@events_bp.route('/<int:event_id>/status', methods=['PATCH'])
@jwt_required
@roles_required('ADMIN')
def update_event_status(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json() or {}
    status = data.get('status')
    if not status:
        return jsonify({'error': 'status is required.'}), 400

    event.event_status = status.upper()
    db.session.commit()
    return jsonify(event.to_dict()), 200


# Module 7
@events_bp.route('/<int:event_id>/schedule', methods=['POST'])
@jwt_required
@roles_required('ADMIN', 'FACULTY')
def add_schedule(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json() or {}

    activity = (data.get("activity") or "").strip()
    schedule_time = (data.get("time") or "").strip()

    if not activity:
        return jsonify({"error": "Activity is required."}), 400

    schedule = EventSchedule(
        event_id=event.id,
        time=schedule_time or "10:00 AM",
        activity=activity,
    )

    db.session.add(schedule)
    db.session.commit()

    return jsonify(schedule.to_dict()), 201


@events_bp.route('/<int:event_id>/announcements', methods=['POST'])
@jwt_required
@roles_required('ADMIN', 'FACULTY')
def add_announcement(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.get_json() or {}

    title = (data.get("title") or "").strip()
    message = (data.get("message") or "").strip()

    if not title:
        return jsonify({"error": "Title is required."}), 400

    announcement = Announcement(
        event_id=event.id,
        title=title,
        message=message,
    )

    db.session.add(announcement)
    db.session.commit()

    return jsonify(announcement.to_dict()), 201


@events_bp.route('/<int:event_id>/attendance', methods=['POST'])
@jwt_required
@roles_required('ADMIN', 'FACULTY')
def post_attendance(event_id):
    Event.query.get_or_404(event_id)

    data = request.get_json() or {}

    student_id = data.get("studentId")
    status = (data.get("status") or "Present").strip()

    if not student_id:
        return jsonify({"error": "studentId is required."}), 400

    attendance = Attendance.query.filter_by(
        event_id=event_id,
        student_id=student_id,
    ).first()

    if attendance:
        attendance.status = status
    else:
        attendance = Attendance(
            event_id=event_id,
            student_id=student_id,
            status=status,
        )
        db.session.add(attendance)

    db.session.commit()

    return jsonify(attendance.to_dict()), 200
