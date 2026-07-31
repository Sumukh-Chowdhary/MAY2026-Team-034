from flask import Blueprint, request, jsonify, g
from datetime import datetime
from collections.abc import Iterable

from app.models import db
from app.models.tickets import (
    ActionTicket,
    ActionTicketApproval,
    ActionTicketType,
    ApprovalStatus,
    TaskStatus,
    resolve_admin,
    resolve_principal
)
from app.utils.auth_jwt import jwt_required

action_tickets_bp = Blueprint("action_tickets", __name__, url_prefix="/api/action-tickets")

VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH"}
VALID_ACTION_TYPES = {
    ActionTicketType.CREATE_CLUB,
    ActionTicketType.CREATE_EVENT_GENERAL,
    ActionTicketType.CREATE_EVENT_FOR_CLUB,
    ActionTicketType.EDIT_CLUB_ADMIN,
    ActionTicketType.EDIT_EVENT_ADMIN
}

def get_user_role(user):
    return user.role.name.upper()

# ---------------------------------------------------------------------------
# WORKFLOW ENGINE FOR ACTION TICKETS (Phase 4 Completed)
# ---------------------------------------------------------------------------
def flatten_approvers(approver_mixed_list):
    flat_list = []
    for item, role in approver_mixed_list:
        if item is None: continue
        if isinstance(item, Iterable) and not isinstance(item, str):
            for u in item:
                if u is not None: flat_list.append((u, role))
        else:
            flat_list.append((item, role))
    return flat_list

def get_approvers_for_action(ticket):
    """Workflow rules for Action Tickets."""
    if ticket.ticket_type == ActionTicketType.CREATE_CLUB:
        return [
            (resolve_principal(), "PRINCIPAL"), 
            (resolve_admin(), "ADMIN")
        ]
    # Default fallback: Just requires Admin approval
    return [(resolve_admin(), "ADMIN")]

def build_action_approval_chain(ticket):
    raw_approvers = get_approvers_for_action(ticket)
    final_approvers = flatten_approvers(raw_approvers)
    
    if not final_approvers:
        return False
        
    for order, (approver, role) in enumerate(final_approvers, start=1):
        ticket.add_approval_step(approver_id=approver.id, approval_role=role, order=order)
    return True

# ---------------------------------------------------------------------------
# TICKET CREATION & LISTING
# ---------------------------------------------------------------------------

@action_tickets_bp.route("", methods=["POST"])
@jwt_required
def create_action_ticket():
    user = g.current_user
    data = request.get_json() or {}

    ticket_type = data.get("ticketType")
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    priority = (data.get("priority") or "MEDIUM").upper()

    if not title: return jsonify({"success": False, "error": "Title is required."}), 400
    if ticket_type not in VALID_ACTION_TYPES: return jsonify({"success": False, "error": "Invalid ticket type."}), 400
    if priority not in VALID_PRIORITIES: return jsonify({"success": False, "error": "Invalid priority."}), 400

    try:
        ticket = ActionTicket(
            raised_by_id=user.id,
            ticket_type=ticket_type,
            title=title,
            description=description,
            priority=priority,
            reference_type=data.get("referenceType"),
            reference_id=data.get("referenceId"),
            reference_name=data.get("referenceName")
        )
        db.session.add(ticket)
        db.session.flush() # Secure ticket.id before adding approvals

        custom_approvers = data.get("approvers")
        if custom_approvers and isinstance(custom_approvers, list) and len(custom_approvers) > 0:
            for order, app_info in enumerate(custom_approvers, start=1):
                appr_id = app_info.get("approverId") or app_info.get("id")
                appr_role = app_info.get("role") or "APPROVER"
                if appr_id:
                    ticket.add_approval_step(approver_id=int(appr_id), approval_role=appr_role, order=order)
        else:
            if not build_action_approval_chain(ticket):
                db.session.rollback()
                return jsonify({"success": False, "error": "Workflow error: No approvers resolved."}), 500

        db.session.commit()
        return jsonify({"success": True, "message": "Action Ticket raised successfully.", "data": ticket.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@action_tickets_bp.route("", methods=["GET"])
@jwt_required
def get_action_tickets():
    user = g.current_user
    role = get_user_role(user)

    query = ActionTicket.query
    if role != "ADMIN" and role != "FACULTY":
        # Students only see their own tickets
        query = query.filter_by(raised_by_id=user.id)
    elif role == "FACULTY":
        # Faculty see tickets they raised, or tickets tagged for them
        faculty_tickets = ActionTicket.tagged_for_faculty(user.id)
        return jsonify({"success": True, "count": len(faculty_tickets), "data": [t.to_dict() for t in faculty_tickets]}), 200

    status = request.args.get("status")
    if status:
        query = query.filter_by(approval_status=status.upper())

    tickets = query.order_by(ActionTicket.created_at.desc()).all()
    return jsonify({"success": True, "count": len(tickets), "data": [t.to_dict() for t in tickets]}), 200

@action_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@jwt_required
def get_action_ticket(ticket_id):
    ticket = ActionTicket.query.get(ticket_id)
    if not ticket: return jsonify({"success": False, "error": "Ticket not found."}), 404
    return jsonify({"success": True, "data": ticket.to_dict()}), 200

# ---------------------------------------------------------------------------
# TASK EXECUTION (The "To-Do List" Phase)
# ---------------------------------------------------------------------------

@action_tickets_bp.route("/<int:ticket_id>/task", methods=["PATCH"])
@jwt_required
def update_task_status(ticket_id):
    """For whoever is assigned to the task to mark it In Progress or Complete."""
    user = g.current_user
    data = request.get_json() or {}
    action = data.get("action")
    remarks = data.get("remarks")

    ticket = ActionTicket.query.get(ticket_id)
    if not ticket: return jsonify({"success": False, "error": "Ticket not found."}), 404

    # Ensure only the assigned person (or an Admin) can update the task
    if ticket.assigned_to_id != user.id and get_user_role(user) != "ADMIN":
        return jsonify({"success": False, "error": "Not authorized to execute this task."}), 403

    if ticket.approval_status != ApprovalStatus.APPROVED:
        return jsonify({"success": False, "error": "Ticket is not approved yet."}), 400

    try:
        if action == "START":
            ticket.start_task(performed_by_id=user.id)
        elif action == "COMPLETE":
            ticket.complete_task(performed_by_id=user.id, remarks=remarks)

            if ticket.ticket_type == ActionTicketType.CREATE_CLUB:
                existing_club = Club.query.filter_by(club_name=ticket.title).first()
                if not existing_club:
                    new_club = Club(
                        club_name=ticket.title,
                        club_description=ticket.description or "Newly created club",
                        club_category="TECHNICAL",
                        club_logo="groups",
                        club_status="ACTIVE",
                        total_members=1,
                        active_members=1
                    )
                    db.session.add(new_club)
                    db.session.flush()

                    creator = User.query.get(ticket.raised_by_id)
                    if creator and creator.role and creator.role.name == "FACULTY":
                        db.session.add(ClubFaculty(club_id=new_club.id, faculty_id=creator.id, faculty_role="FACULTY_COORDINATOR"))
                    elif creator and creator.role and creator.role.name == "STUDENT":
                        db.session.add(ClubOrganizer(club_id=new_club.id, user_id=creator.id, organizer_role="PRESIDENT"))
        else:
            return jsonify({"success": False, "error": "Invalid action."}), 400

        db.session.commit()
        return jsonify({"success": True, "message": f"Task {action.lower()}ed.", "data": ticket.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Unable to update task."}), 500

# ---------------------------------------------------------------------------
# APPROVAL WORKFLOW ROUTES
# ---------------------------------------------------------------------------

@action_tickets_bp.route("/<int:ticket_id>/approve", methods=["POST"])
@jwt_required
def approve_action(ticket_id):
    user = g.current_user
    ticket = ActionTicket.query.get(ticket_id)
    
    if not ticket: return jsonify({"success": False, "error": "Ticket not found."}), 404
    
    approval = ActionTicketApproval.query.filter_by(action_ticket_id=ticket.id, approver_id=user.id, status=ApprovalStatus.PENDING).first()
    if not approval: return jsonify({"success": False, "error": "Not authorized to approve this."}), 403

    try:
        approval.status = ApprovalStatus.APPROVED
        approval.approved_at = datetime.utcnow()

        remaining = ActionTicketApproval.query.filter_by(action_ticket_id=ticket.id, status=ApprovalStatus.PENDING).count()
        if remaining == 0:
            # All approvals done! Open the task and assign it to an Admin to execute.
            admin = resolve_admin()
            ticket.mark_approved_and_open_task(assigned_to_id=admin.id if admin else user.id)

        db.session.commit()
        return jsonify({"success": True, "message": "Approved successfully.", "data": ticket.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Failed to approve."}), 500

@action_tickets_bp.route("/<int:ticket_id>/reject", methods=["POST"])
@jwt_required
def reject_action(ticket_id):
    user = g.current_user
    data = request.get_json() or {}
    ticket = ActionTicket.query.get(ticket_id)

    approval = ActionTicketApproval.query.filter_by(action_ticket_id=ticket.id, approver_id=user.id, status=ApprovalStatus.PENDING).first()
    if not approval: return jsonify({"success": False, "error": "Not authorized."}), 403

    try:
        approval.status = ApprovalStatus.REJECTED
        approval.remarks = data.get("remarks")
        approval.approved_at = datetime.utcnow()
        ticket.approval_status = ApprovalStatus.REJECTED

        db.session.commit()
        return jsonify({"success": True, "message": "Rejected.", "data": ticket.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Failed to reject."}), 500

@action_tickets_bp.route("/<int:ticket_id>/request-changes", methods=["POST"])
@jwt_required
def request_changes_action(ticket_id):
    user = g.current_user
    data = request.get_json() or {}
    ticket = ActionTicket.query.get(ticket_id)

    approval = ActionTicketApproval.query.filter_by(action_ticket_id=ticket.id, approver_id=user.id, status=ApprovalStatus.PENDING).first()
    if not approval: return jsonify({"success": False, "error": "Not authorized."}), 403

    try:
        approval.status = ApprovalStatus.CHANGES_REQUESTED
        approval.remarks = data.get("remarks")
        approval.approved_at = datetime.utcnow()
        ticket.approval_status = ApprovalStatus.CHANGES_REQUESTED

        db.session.commit()
        return jsonify({"success": True, "message": "Changes requested.", "data": ticket.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Failed to request changes."}), 500

@action_tickets_bp.route("/<int:ticket_id>/approvals", methods=["GET"])
@jwt_required
def get_action_approvals(ticket_id):
    approvals = ActionTicketApproval.query.filter_by(action_ticket_id=ticket_id).order_by(ActionTicketApproval.approval_order).all()
    return jsonify({"success": True, "count": len(approvals), "data": [a.to_dict() for a in approvals]}), 200

@action_tickets_bp.route("/<int:ticket_id>/resubmit", methods=["POST"])
@jwt_required
def resubmit_action_ticket(ticket_id):
    user = g.current_user
    ticket = ActionTicket.query.get(ticket_id)
    if not ticket: return jsonify({"success": False, "error": "Ticket not found."}), 404
    if ticket.raised_by_id != user.id:
        return jsonify({"success": False, "error": "Only the creator can resubmit."}), 403

    data = request.get_json() or {}
    if data.get("title"): ticket.title = data.get("title").strip()
    if data.get("description") is not None: ticket.description = data.get("description").strip()
    if data.get("priority"): ticket.priority = data.get("priority").upper()

    try:
        ticket.resubmit()
        custom_approvers = data.get("approvers")
        if custom_approvers and isinstance(custom_approvers, list) and len(custom_approvers) > 0:
            for order, app_info in enumerate(custom_approvers, start=1):
                appr_id = app_info.get("approverId") or app_info.get("id")
                appr_role = app_info.get("role") or "APPROVER"
                if appr_id:
                    ticket.add_approval_step(approver_id=int(appr_id), approval_role=appr_role, order=order)
        else:
            if not build_action_approval_chain(ticket):
                db.session.rollback()
                return jsonify({"success": False, "error": "Workflow error: Could not rebuild approval chain."}), 500

        db.session.commit()
        return jsonify({"success": True, "message": f"Action ticket resubmitted successfully (Version v{ticket.version}).", "data": ticket.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Resubmit failed: {str(e)}"}), 500