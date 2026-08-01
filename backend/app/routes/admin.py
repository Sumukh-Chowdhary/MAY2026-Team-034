from app.services.club_service import (
    archive_club as archive_club_service,
    deactivate_club_member as deactivate_club_member_service,
    get_all_clubs as get_all_clubs_service,
    get_club_by_id as get_club_by_id_service,
    get_club_events as get_club_events_service,
    get_club_member as get_club_member_service,
    get_club_members as get_club_members_service,
    get_faculty_details as get_faculty_details_service,
    update_club_status as update_club_status_service,
    update_club as update_club_service,
    create_club as create_club_service
)

from app.models import db
from flask import Blueprint, request, jsonify
from app.utils.auth_jwt import jwt_required, roles_required
from werkzeug.exceptions import NotFound

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.get('/clubs')
@jwt_required
@roles_required('ADMIN')
def get_clubs():
    return jsonify(get_all_clubs_service()), 200

@admin_bp.get("/clubs/<int:club_id>")
@jwt_required
@roles_required("ADMIN")
def get_club(club_id):
    return jsonify(get_club_by_id_service(club_id)), 200

@admin_bp.route("/clubs/<int:club_id>/status", methods=["PATCH"])
@jwt_required
@roles_required("ADMIN")
def update_club_status(club_id):
    data = request.get_json() or {}

    try:
        club = update_club_status_service(
            club_id,
            data.get("status")
        )
        return jsonify(club), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

@admin_bp.get("/clubs/faculty-details")
@jwt_required
@roles_required("ADMIN")
def get_faculty_details():
    return jsonify(get_faculty_details_service()), 200

@admin_bp.post("/clubs/create")
@jwt_required
@roles_required("ADMIN")
def create_club():
    data = request.get_json() or {}

    try:

        club = create_club_service(
            name=(data.get("name") or "").strip(),
            category=(data.get("category") or "").strip(),
            description=(data.get("description") or "").strip(),
            logo=data.get("logo"),
            faculty_ids=data.get("facultyCoordinatorIds", [])
        )

        return jsonify(club), 201

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
            "error": "Failed to create club.",
            "details": str(e)
        }), 500

@admin_bp.put("/clubs/<int:club_id>/edit")
@jwt_required
@roles_required("ADMIN")
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

@admin_bp.delete("/clubs/<int:club_id>")
@jwt_required
@roles_required("ADMIN")
def archive_club(club_id):
    try:
        club = archive_club_service(club_id)
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
            "error": "Failed to archive club.",
            "details": str(e)
        }), 500

@admin_bp.get("/clubs/<int:club_id>/members")
@jwt_required
@roles_required("ADMIN")
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

@admin_bp.get("/clubs/<int:club_id>/members/<int:user_id>")
@jwt_required
@roles_required("ADMIN")
def get_club_member(club_id, user_id):
    try:
        member = get_club_member_service(
            club_id,
            user_id
        )
        return jsonify(member), 200

    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

@admin_bp.patch("/clubs/<int:club_id>/members/<int:user_id>/deactivate")
@jwt_required
@roles_required("ADMIN")
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

@admin_bp.get("/clubs/<int:club_id>/events")
@jwt_required
@roles_required("ADMIN")
def get_club_events(club_id):
    return jsonify(
        get_club_events_service(club_id)
    ), 200

