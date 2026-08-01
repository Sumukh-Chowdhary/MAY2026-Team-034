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
from flask import Blueprint, request, jsonify
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


