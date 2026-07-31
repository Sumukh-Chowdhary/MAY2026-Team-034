from flask import Blueprint, jsonify, g
from sqlalchemy import desc

from app.models import db
from app.models.tickets import (
    Request, RequestApproval, 
    ActionTicket, ActionTicketApproval, 
    ApprovalStatus
)
from app.utils.auth_jwt import jwt_required

# Note the root prefix; we define the full paths in the routes below
request_views_bp = Blueprint("request_views", __name__, url_prefix="/api")

def get_user_role(user):
    return user.role.name.upper()

@request_views_bp.route("/student/requests/dashboard", methods=["GET"])
@jwt_required
def get_student_requests_dashboard():
    """Powers the Student 'Requests' UI tab."""
    user = g.current_user
    if get_user_role(user) != "STUDENT":
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # Fetch both Requests and Action Tickets raised by the student
    my_requests = Request.query.filter_by(requester_id=user.id).order_by(desc(Request.created_at)).all()
    my_action_tickets = ActionTicket.query.filter_by(raised_by_id=user.id).order_by(desc(ActionTicket.created_at)).all()

    return jsonify({
        "success": True,
        "data": {
            "myTickets": [r.to_dict() for r in my_requests] + [t.to_dict() for t in my_action_tickets]
        }
    }), 200

@request_views_bp.route("/faculty/requests/dashboard", methods=["GET"])
@jwt_required
def get_faculty_requests_dashboard():
    """Powers the Faculty 'Requests' UI tab."""
    user = g.current_user
    if get_user_role(user) not in {"FACULTY", "ADMIN"}:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # --- TAB 1: My Tickets (Raised by them) ---
    my_requests = Request.query.filter_by(requester_id=user.id).order_by(desc(Request.created_at)).all()
    my_action_tickets = ActionTicket.query.filter_by(raised_by_id=user.id).order_by(desc(ActionTicket.created_at)).all()
    my_tickets_combined = [r.to_dict() for r in my_requests] + [t.to_dict() for t in my_action_tickets]

    # --- TAB 2: Incoming Requests (Assigned to them to approve) ---
    pending_req_approvals = RequestApproval.query.filter_by(approver_id=user.id, status=ApprovalStatus.PENDING).all()
    pending_act_approvals = ActionTicketApproval.query.filter_by(approver_id=user.id, status=ApprovalStatus.PENDING).all()

    incoming_requests_combined = [a.request.to_dict() for a in pending_req_approvals if a.request] + \
                                 [a.action_ticket.to_dict() for a in pending_act_approvals if a.action_ticket]

    return jsonify({
        "success": True,
        "data": {
            "myTickets": my_tickets_combined,
            "incomingRequests": incoming_requests_combined
        }
    }), 200

@request_views_bp.route("/admin/requests/dashboard", methods=["GET"])
@jwt_required
def get_admin_requests_dashboard():
    """Powers the Admin 'Requests' UI tab."""
    user = g.current_user
    if get_user_role(user) != "ADMIN":
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # --- TAB 1: Club Requests ---
    club_requests = Request.query.filter_by(reference_type="CLUB", workflow_status=ApprovalStatus.PENDING).order_by(desc(Request.created_at)).all()
    club_actions = ActionTicket.query.filter_by(reference_type="CLUB", approval_status=ApprovalStatus.PENDING).order_by(desc(ActionTicket.created_at)).all()
    
    # --- TAB 2: Event Requests ---
    event_requests = Request.query.filter_by(reference_type="EVENT", workflow_status=ApprovalStatus.PENDING).order_by(desc(Request.created_at)).all()
    event_actions = ActionTicket.query.filter_by(reference_type="EVENT", approval_status=ApprovalStatus.PENDING).order_by(desc(ActionTicket.created_at)).all()

    return jsonify({
        "success": True,
        "data": {
            "clubRequests": [r.to_dict() for r in club_requests] + [t.to_dict() for t in club_actions],
            "eventRequests": [r.to_dict() for r in event_requests] + [t.to_dict() for t in event_actions]
        }
    }), 200