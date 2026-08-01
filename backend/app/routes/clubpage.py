from app.services.club_service import (
    get_all_clubs as get_all_clubs_service,
    get_club_by_id as get_club_by_id_service,
    get_club_events as get_club_events_service,
    get_club_members as get_club_members_service,
)

from app.models import db
from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound

club_bp = Blueprint(
    "club",
    __name__,
    url_prefix="/api"
)

@club_bp.get('/clubs')
def get_clubs():
    return jsonify(get_all_clubs_service()), 200

@club_bp.get("/clubs/<int:club_id>")
def get_club(club_id):
    try:
        club = get_club_by_id_service(club_id)
        return jsonify(club), 200
    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

@club_bp.get("/clubs/<int:club_id>/members")
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

@club_bp.get("/clubs/<int:club_id>/events")
def get_club_events(club_id):

    try:
        events = get_club_events_service(club_id)
        return jsonify(events), 200
    except NotFound as e:
        return jsonify({
            "error": e.description
        }), 404

