from flask import Blueprint, request, jsonify, g
from datetime import datetime

from app.models import db
from app.models.tickets import (
    AssignmentTicket, 
    AssignmentStatus, 
    AssignmentDuration
)
from app.utils.auth_jwt import jwt_required

assignments_bp = Blueprint("assignments", __name__, url_prefix="/api/assignment-tickets")

def get_user_role(user):
    return user.role.name.upper()

# ---------------------------------------------------------------------------
# GET /api/assignment-tickets
# ---------------------------------------------------------------------------
@assignments_bp.route("", methods=["GET"])
@jwt_required
def get_all_assignments():
    """Admin view to see all assignments, with optional filtering."""
    user = g.current_user
    if get_user_role(user) != "ADMIN":
        return jsonify({"success": False, "error": "Only admins can view all assignment tickets."}), 403

    status = request.args.get("status")
    role = request.args.get("role")

    query = AssignmentTicket.query

    if status:
        query = query.filter_by(status=status.upper())
    if role:
        query = query.filter_by(assignment_role=role.upper())

    tickets = query.order_by(AssignmentTicket.created_at.desc()).all()
    
    # Optional: trigger expiry check on fetch to keep data fresh
    for t in tickets:
        t.check_expiry()
    db.session.commit()

    return jsonify({"success": True, "count": len(tickets), "data": [t.to_dict() for t in tickets]}), 200

# ---------------------------------------------------------------------------
# GET /api/assignment-tickets/<id>
# ---------------------------------------------------------------------------
@assignments_bp.route("/<int:ticket_id>", methods=["GET"])
@jwt_required
def get_assignment(ticket_id):
    """View details of a specific assignment ticket."""
    user = g.current_user
    ticket = AssignmentTicket.query.get(ticket_id)

    if not ticket:
        return jsonify({"success": False, "error": "Assignment ticket not found."}), 404

    # Only Admin or the ticket holder can view
    if get_user_role(user) != "ADMIN" and ticket.holder_id != user.id:
        return jsonify({"success": False, "error": "Not authorized to view this ticket."}), 403

    ticket.check_expiry()
    db.session.commit()

    return jsonify({"success": True, "data": ticket.to_dict()}), 200

# ---------------------------------------------------------------------------
# PATCH /api/assignment-tickets/<id>
# ---------------------------------------------------------------------------
@assignments_bp.route("/<int:ticket_id>", methods=["PATCH"])
@jwt_required
def update_assignment(ticket_id):
    """Admin action to Suspend, Reactivate, Terminate, or Edit Duration."""
    user = g.current_user
    if get_user_role(user) != "ADMIN":
        return jsonify({"success": False, "error": "Only admins can modify assignment tickets."}), 403

    ticket = AssignmentTicket.query.get(ticket_id)
    if not ticket:
        return jsonify({"success": False, "error": "Assignment ticket not found."}), 404

    data = request.get_json() or {}
    action = data.get("action")
    remarks = data.get("remarks")

    if not action:
        return jsonify({"success": False, "error": "Action is required."}), 400

    action = action.upper()
    try:
        if action == "SUSPEND":
            if ticket.status != AssignmentStatus.ACTIVE:
                return jsonify({"success": False, "error": "Only active assignments can be suspended."}), 400
            ticket.suspend(performed_by_id=user.id, remarks=remarks)

        elif action == "REACTIVATE":
            if ticket.status != AssignmentStatus.SUSPENDED:
                return jsonify({"success": False, "error": "Only suspended assignments can be reactivated."}), 400
            ticket.reactivate(performed_by_id=user.id, remarks=remarks)

        elif action == "TERMINATE":
            ticket.terminate(performed_by_id=user.id, remarks=remarks)

        elif action == "EDIT_DURATION":
            duration_type = data.get("durationType")
            ends_at_str = data.get("endsAt")
            
            if duration_type not in {AssignmentDuration.INDEFINITE, AssignmentDuration.DATE_RANGE}:
                return jsonify({"success": False, "error": "Invalid duration type."}), 400
                
            ends_at = None
            if duration_type == AssignmentDuration.DATE_RANGE and ends_at_str:
                ends_at = datetime.fromisoformat(ends_at_str.replace("Z", "+00:00"))
                
            ticket.edit_duration(performed_by_id=user.id, duration_type=duration_type, ends_at=ends_at, remarks=remarks)

        else:
            return jsonify({"success": False, "error": "Invalid action."}), 400

        db.session.commit()
        return jsonify({"success": True, "message": f"Assignment {action.lower()}d successfully.", "data": ticket.to_dict()}), 200

    except ValueError as e:
        return jsonify({"success": False, "error": f"Date format error: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Unable to update assignment ticket."}), 500

# ---------------------------------------------------------------------------
# GET /api/assignment-tickets/user/<id>
# ---------------------------------------------------------------------------
@assignments_bp.route("/user/<int:target_user_id>", methods=["GET"])
@jwt_required
def get_user_assignments(target_user_id):
    """View all assignments (active and past) for a specific user."""
    user = g.current_user
    
    if get_user_role(user) != "ADMIN" and user.id != target_user_id:
        return jsonify({"success": False, "error": "Not authorized to view these tickets."}), 403

    active_tickets = AssignmentTicket.current_for(target_user_id)
    history_tickets = AssignmentTicket.history_for(target_user_id)
    
    # Run expiry checks on active ones
    for t in active_tickets:
        t.check_expiry()
    db.session.commit()

    return jsonify({
        "success": True, 
        "data": {
            "active": [t.to_dict() for t in active_tickets if t.status == AssignmentStatus.ACTIVE],
            "history": [t.to_dict() for t in history_tickets] + [t.to_dict() for t in active_tickets if t.status != AssignmentStatus.ACTIVE]
        }
    }), 200

# ---------------------------------------------------------------------------
# POST /api/assignment-tickets/<id>/leave
# ---------------------------------------------------------------------------
@assignments_bp.route("/<int:ticket_id>/leave", methods=["POST"])
@jwt_required
def leave_assignment(ticket_id):
    """Allows the assignment ticket holder to step down/leave their role."""
    user = g.current_user
    ticket = AssignmentTicket.query.get(ticket_id)

    if not ticket:
        return jsonify({"success": False, "error": "Assignment ticket not found."}), 404

    if ticket.holder_id != user.id and get_user_role(user) != "ADMIN":
        return jsonify({"success": False, "error": "Not authorized to step down from this role."}), 403

    if ticket.status != AssignmentStatus.ACTIVE:
        return jsonify({"success": False, "error": "Role assignment is not active."}), 400

    try:
        ticket.terminate(performed_by_id=user.id, remarks="User stepped down from role")
        
        # Clean up corresponding club membership/organizer record
        if ticket.reference_type == "CLUB" and ticket.reference_id:
            from app.models.club import ClubOrganizer, ClubMembership
            if ticket.assignment_role in {"ORGANIZER", "PRESIDENT"}:
                org = ClubOrganizer.query.filter_by(club_id=ticket.reference_id, user_id=ticket.holder_id).first()
                if org:
                    db.session.delete(org)
            elif ticket.assignment_role in {"VOLUNTEER", "MEMBER"}:
                mem = ClubMembership.query.filter_by(club_id=ticket.reference_id, user_id=ticket.holder_id).first()
                if mem:
                    mem.membership_status = "INACTIVE"

        db.session.commit()
        return jsonify({"success": True, "message": "Successfully left role.", "data": ticket.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Failed to leave role."}), 500