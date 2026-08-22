from flask import Blueprint, request, jsonify
from app.models import db
from app.models.events import Venue
from app.utils.auth_jwt import jwt_required, roles_required
from app.utils.cache import get_cached, set_cached, delete_cached

venues_bp = Blueprint('venues', __name__, url_prefix='/api/venues')

@venues_bp.route('', methods=['GET'])
@jwt_required
def get_venues():
    search_q = request.args.get('search')

    # Only use the "all venues" cache when there is no search filter.
    if not search_q:
        cache_key = "venues:all"

        cached = get_cached(cache_key)

        if cached is not None:
            print("Redis cache HIT:", cache_key)
            return jsonify(cached), 200

        print("Redis cache MISS:", cache_key)

    query = Venue.query

    if search_q:
        q = f"%{search_q.strip().lower()}%"
        query = query.filter(
            db.or_(
                db.func.lower(Venue.venue_name).like(q),
                db.func.lower(Venue.venue_location).like(q),
                db.func.lower(Venue.venue_type).like(q)
            )
        )

    venues = query.order_by(Venue.venue_name.asc()).all()

    result = [venue.to_dict() for venue in venues]

    # Only cache the unfiltered list for now.
    if not search_q:
        set_cached(cache_key, result)

    return jsonify(result), 200


@venues_bp.route('/calendar', methods=['GET'])
@jwt_required
def get_venue_calendar():
    """
    Returns every venue along with its upcoming bookings (non-cancelled,
    non-completed events) within a date window, so organizers can see at a
    glance which venues are free before submitting a venue request.
    Defaults to the next 30 days; accepts ?days=N to widen/narrow the window.
    """
    from datetime import date, timedelta
    from app.models.events import Event

    try:
        days = int(request.args.get('days', 30))
    except (TypeError, ValueError):
        days = 30
    days = max(1, min(days, 180))

    window_start = date.today()
    window_end = window_start + timedelta(days=days)

    venues = Venue.query.order_by(Venue.venue_name.asc()).all()

    upcoming_events = Event.query.filter(
        Event.venue_id.isnot(None),
        Event.event_status.notin_(['CANCELLED', 'COMPLETED', 'CLOSED']),
        Event.start_date <= window_end,
        Event.end_date >= window_start
    ).order_by(Event.start_date.asc()).all()

    bookings_by_venue = {}
    for ev in upcoming_events:
        bookings_by_venue.setdefault(ev.venue_id, []).append({
            'eventId': ev.id,
            'eventName': ev.event_name,
            'clubName': ev.club.club_name if ev.club else 'General / Institutional',
            'startDate': ev.start_date.isoformat() if ev.start_date else None,
            'endDate': ev.end_date.isoformat() if ev.end_date else None,
            'startTime': ev.start_time.strftime('%H:%M') if ev.start_time else None,
            'endTime': ev.end_time.strftime('%H:%M') if ev.end_time else None,
        })

    result = []
    for v in venues:
        result.append({
            'id': v.id,
            'name': v.venue_name,
            'location': v.venue_location,
            'type': v.venue_type,
            'capacity': v.capacity,
            'availabilityStatus': v.availability_status,
            'bookings': bookings_by_venue.get(v.id, [])
        })

    return jsonify({
        'windowStart': window_start.isoformat(),
        'windowEnd': window_end.isoformat(),
        'venues': result
    }), 200


@venues_bp.route('/<int:venue_id>', methods=['GET'])
@jwt_required
def get_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    return jsonify(venue.to_dict()), 200


@venues_bp.route('/create', methods=['POST'])
@jwt_required
@roles_required('ADMIN')
def create_venue():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    location = (data.get('location') or '').strip()
    venue_type = data.get('type')
    capacity = data.get('capacity')

    if not name:
        return jsonify({'error': 'Venue name is required.'}), 400
    if not location:
        return jsonify({'error': 'Venue location is required.'}), 400
    if capacity is None:
        return jsonify({'error': 'Venue capacity is required.'}), 400

    if Venue.query.filter_by(venue_name=name).first():
        return jsonify({'error': 'A venue with this name already exists.'}), 409

    venue = Venue(
        venue_name=name,
        venue_location=location,
        venue_type=venue_type,
        capacity=capacity,
        availability_status='AVAILABLE'
    )
    db.session.add(venue)
    db.session.commit()

    delete_cached("venues:all")

    return jsonify(venue.to_dict()), 201


@venues_bp.route('/<int:venue_id>/edit', methods=['PUT'])
@jwt_required
@roles_required('ADMIN')
def update_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    data = request.get_json() or {}
    name = data.get('name')
    location = data.get('location')
    venue_type = data.get('type')
    capacity = data.get('capacity')

    if name is not None:
        venue.venue_name = name.strip()
    if location is not None:
        venue.venue_location = location
    if venue_type is not None:
        venue.venue_type = venue_type
    if capacity is not None:
        venue.capacity = capacity

    db.session.commit()

    delete_cached("venues:all")
    delete_cached("events:all")
    
    return jsonify(venue.to_dict()), 200


@venues_bp.route('/<int:venue_id>/status', methods=['PATCH'])
@jwt_required
@roles_required('ADMIN')
def update_venue_status(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    data = request.get_json() or {}
    status = data.get('status')

    if not status:
        return jsonify({'error': 'status is required.'}), 400

    venue.availability_status = status.upper()
    db.session.commit()

    delete_cached("venues:all")
    
    return jsonify(venue.to_dict()), 200


@venues_bp.route('/<int:venue_id>/availability', methods=['GET'])
@jwt_required
def check_venue_availability(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    if venue.availability_status == 'ARCHIVED':
        return jsonify({'available': False, 'reason': 'ARCHIVED', 'conflictingEvent': None}), 200

    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')

    if not start_date_str or not end_date_str:
        return jsonify({'available': True, 'conflictingEvent': None}), 200

    from app.routes.events import _parse_date
    start_d = _parse_date(start_date_str)
    end_d = _parse_date(end_date_str)

    if not start_d or not end_d:
        return jsonify({'available': True, 'conflictingEvent': None}), 200

    from app.models.events import Event
    conflicting_event = Event.query.filter(
        Event.venue_id == venue_id,
        Event.event_status.notin_(['CANCELLED', 'COMPLETED', 'CLOSED']),
        Event.start_date <= end_d,
        Event.end_date >= start_d
    ).first()

    if conflicting_event:
        return jsonify({
            'available': False,
            'conflictingEvent': {
                'id': conflicting_event.id,
                'name': conflicting_event.event_name,
                'club': conflicting_event.club.club_name if conflicting_event.club else 'General',
                'clubName': conflicting_event.club.club_name if conflicting_event.club else 'General',
                'startDate': str(conflicting_event.start_date),
                'endDate': str(conflicting_event.end_date),
                'startTime': str(conflicting_event.start_time) if conflicting_event.start_time else '09:00',
                'endTime': str(conflicting_event.end_time) if conflicting_event.end_time else '17:00'
            }
        }), 200

    return jsonify({'available': True, 'conflictingEvent': None}), 200
