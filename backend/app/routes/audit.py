from flask import Blueprint, jsonify, g
from app.models.tickets import TicketAudit
from app.utils.auth_jwt import jwt_required

audit_bp = Blueprint("audit", __name__, url_prefix="/api/audit")

def get_user_role(user):
    return user.role.name.upper()

# ---------------------------------------------------------------------------
# GET /api/audit/<subject_type>/<subject_id>
# ---------------------------------------------------------------------------
@audit_bp.route("/<string:subject_type>/<int:subject_id>", methods=["GET"])
@jwt_required
def get_ticket_history(subject_type, subject_id):
    """
    Fetches the complete audit timeline for any ticket in the system.
    subject_type must be one of: REQUEST, ASSIGNMENT_TICKET, ACTION_TICKET
    """
    user = g.current_user
    subject_type = subject_type.upper()
    
    valid_subject_types = {"REQUEST", "ASSIGNMENT_TICKET", "ACTION_TICKET"}
    
    if subject_type not in valid_subject_types:
        return jsonify({"success": False, "error": f"Invalid ticket type. Must be one of {valid_subject_types}"}), 400

    # Fetch all logs for this specific ticket, ordered newest to oldest
    logs = TicketAudit.query.filter_by(
        subject_type=subject_type,
        subject_id=subject_id
    ).order_by(TicketAudit.created_at.desc()).all()

    # Optional: You can add an ownership check here to ensure students 
    # only see logs for tickets they actually own or raised.
    # If the user is a student, and the list is empty, it's safer to just return [] anyway.

    return jsonify({
        "success": True, 
        "count": len(logs), 
        "data": [log.to_dict() for log in logs]
    }), 200