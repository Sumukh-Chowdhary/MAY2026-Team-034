from app.services.club_service import (
    deactivate_club_member as deactivate_club_member_service,
    get_all_clubs as get_all_clubs_service,
    get_club_by_id as get_club_by_id_service,
    update_club as update_club_service,
    get_club_events as get_club_events_service,
    get_club_member as get_club_member_service,
    get_club_members as get_club_members_service,
)

from app.models import db
from app.models.club import Club, ClubFaculty
from flask import Blueprint, jsonify, request, g
from app.utils.auth_jwt import jwt_required, roles_required
from app.utils.auth_jwt import faculty_club_access_required
from werkzeug.exceptions import NotFound

faculty_bp = Blueprint('faculty', __name__, url_prefix='/api/faculty')

@faculty_bp.get('/clubs')
@jwt_required
@roles_required('FACULTY')
def get_clubs():
    return jsonify(get_all_clubs_service()), 200

@faculty_bp.get("/clubs/<int:club_id>")
@jwt_required
@roles_required("FACULTY")
def get_club(club_id):
    try:
        club = get_club_by_id_service(club_id)
        return jsonify(club), 200
    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

@faculty_bp.put("/clubs/<int:club_id>/edit")
@jwt_required
@roles_required("FACULTY")
@faculty_club_access_required
def update_club(club_id):

    data = request.get_json() or {}

    try:

        club = update_club_service(
            club_id=club_id,
            name=(data.get("name") or "").strip(),
            category=(data.get("category") or "").strip(),
            description=(data.get("description") or "").strip(),
            logo=data.get("logo"),
            faculty_ids=data.get("facultyCoordinatorIds", [])
        )

        return jsonify(club), 200

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": "Failed to update club.",
            "details": str(e)
        }), 500

@faculty_bp.get("/clubs/<int:club_id>/members")
@jwt_required
@roles_required("FACULTY")
def get_club_members(club_id):

    try:
        members = get_club_members_service(
            club_id,
            include_inactive=True
        )
        return jsonify(members), 200
    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

@faculty_bp.get("/clubs/<int:club_id>/members/<int:user_id>")
@jwt_required
@roles_required("FACULTY")
def get_club_member(club_id, user_id):

    try:
        member = get_club_member_service(club_id, user_id)
        return jsonify(member), 200
    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

@faculty_bp.patch("/clubs/<int:club_id>/members/<int:user_id>/deactivate")
@jwt_required
@roles_required("FACULTY")
@faculty_club_access_required
def deactivate_club_member(club_id, user_id):

    try:

        member = deactivate_club_member_service(
            club_id,
            user_id
        )

        return jsonify(member), 200

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": "Failed to deactivate member.",
            "details": str(e)
        }), 500

@faculty_bp.get("/clubs/<int:club_id>/events")
@jwt_required
@roles_required("FACULTY")
def get_club_events(club_id):

    try:
        events = get_club_events_service(club_id)
        return jsonify(events), 200
    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

@faculty_bp.get("/my-clubs")
@jwt_required
@roles_required("FACULTY")
def get_my_supervised_clubs():
    # Retrieve all ClubFaculty entries for this user
    faculty_entries = ClubFaculty.query.filter_by(faculty_id=g.current_user.id).all()
    
    my_clubs = []
    for entry in faculty_entries:
        club = entry.club
        if not club:
            continue
        
        # Get assigned students (e.g. organizers/members)
        assigned_students = [
            {"id": org.user.id, "name": org.user.email.split('@')[0], "role": org.organizer_role}
            for org in club.organizers
        ]
        
        # Get events for this club
        events_list = [
            {"id": ev.id, "name": ev.event_name, "status": ev.event_status}
            for ev in club.events
        ]
        
        my_clubs.append({
            "id": club.id,
            "clubName": club.club_name,
            "roleTitle": entry.faculty_role,
            "assignedStudents": assigned_students,
            "events": events_list
        })
        
    return jsonify(my_clubs), 200

@faculty_bp.route("/clubs/<int:club_id>/leave", methods=["POST"])
@jwt_required
@roles_required("FACULTY")
def step_down_from_club(club_id):
    club = Club.query.get(club_id)
    if not club:
        return jsonify({"error": "Club not found"}), 404
        
    # Check if the faculty coordinator has access to this club
    entry = ClubFaculty.query.filter_by(club_id=club_id, faculty_id=g.current_user.id).first()
    if not entry:
        return jsonify({"error": "You are not a coordinator for this club"}), 403
        
    try:
        db.session.delete(entry)
        db.session.commit()
        return jsonify({"message": "Stepped down from club coordinator role successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to step down", "details": str(e)}), 500


