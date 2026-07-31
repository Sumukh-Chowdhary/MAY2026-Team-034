from app.services.club_service import archive_club, deactivate_club_member, get_all_clubs, get_club_events, get_club_member, get_club_members, update_club_status, get_faculty_details
from backend.app.models import db
from flask import Blueprint, request, jsonify
from app.utils.auth_jwt import jwt_required, roles_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@jwt_required
@roles_required('ADMIN')
@admin_bp.get('/clubs')
def get_clubs():
    return jsonify(get_all_clubs()), 200

@jwt_required
@roles_required("ADMIN")
@admin_bp.route("/clubs/<int:club_id>/status", methods=["PATCH"])
def update_club_status(club_id):
    data = request.get_json() or {}

    try:
        club = update_club_status(
            club_id,
            data.get("status")
        )
        return jsonify(club), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

@jwt_required
@roles_required("ADMIN")
@admin_bp.get("/clubs/faculty-details")
def get_faculty_details():
    return jsonify(get_faculty_details()), 200

@jwt_required
@roles_required("ADMIN")
@admin_bp.post("/clubs/create")
def create_club():
    data = request.get_json() or {}

    try:

        club = create_club(
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

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": "Failed to create club.",
            "details": str(e)
        }), 500

@jwt_required
@roles_required("ADMIN")
@admin_bp.put("/clubs/<int:club_id>/edit")
def update_club(club_id):

    data = request.get_json() or {}

    try:

        club = update_club(
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

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": "Failed to update club.",
            "details": str(e)
        }), 500

@jwt_required
@roles_required("ADMIN")
@admin_bp.delete("/clubs/<int:club_id>")
def archive_club(club_id):

    try:
        club = archive_club(club_id)
        return jsonify(club), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to archive club.",
            "details": str(e)
        }), 500

@jwt_required
@roles_required("ADMIN")
@admin_bp.get("/clubs/<int:club_id>/members")
def get_club_members(club_id):
    return jsonify(
        get_club_members(
            club_id,
            include_inactive=True
        )
    ), 200

@jwt_required
@roles_required("ADMIN")
@admin_bp.get("/clubs/<int:club_id>/members/<int:user_id>")
def get_club_member(club_id, user_id):
    return jsonify(
        get_club_member(
            club_id,
            user_id
        )
    ), 200

@jwt_required
@roles_required("ADMIN")
@admin_bp.patch("/clubs/<int:club_id>/members/<int:user_id>/deactivate")
def deactivate_club_member(club_id, user_id):

    try:

        member = deactivate_club_member(
            club_id,
            user_id
        )

        return jsonify(member), 200

    except ValueError as e:

        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "error": "Failed to deactivate member.",
            "details": str(e)
        }), 500

@jwt_required
@roles_required("ADMIN")
@admin_bp.get("/clubs/<int:club_id>/events")
def get_club_events(club_id):
    return jsonify(
        get_club_events(club_id)
    ), 200

