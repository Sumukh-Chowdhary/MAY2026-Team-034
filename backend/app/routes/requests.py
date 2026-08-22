from flask import Blueprint, request, jsonify, g
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from collections.abc import Iterable

from app.models import db
from app.models.tickets import (
    Request,
    RequestApproval,
    RequestType,
    ActionTicket,
    ActionTicketApproval,
    ActionTicketType,
    AssignmentTicket,
    AssignmentRole,
    AssignmentDuration,
    AssignmentStatus,
    ApprovalStatus,
    TicketAudit,
    resolve_admin,
    resolve_principal,
    resolve_club_faculty
)
from app.models.club import Club, ClubOrganizer, ClubFaculty
from app.utils.auth_jwt import jwt_required, check_legacy_user_action
from app.services.notification_service import NotificationService

requests_bp = Blueprint("requests", __name__, url_prefix="/api/requests")

VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH"}

VALID_REQUEST_TYPES = (
    RequestType.ASSIGNMENT_TYPES |
    RequestType.APPROVAL_ONLY_TYPES
)

def resolve_finance_committee(): return []
def resolve_dean_student_affairs(): return None
def resolve_sports_faculty(): return None
def resolve_security_officer(): return None

def flatten_approvers(approver_mixed_list):
    """
    Takes a mixed list of (User/Iterable, "ROLE_NAME") tuples,
    flattens lists, and filters out None values.
    Returns: List of (User, "ROLE_NAME")
    """
    flat_list = []
    for item, role in approver_mixed_list:
        if item is None:
            continue
        
        # If the item is a list of users
        if isinstance(item, Iterable) and not isinstance(item, str):
            for u in item:
                if u is not None:
                    flat_list.append((u, role))
        else:
            # Single user
            flat_list.append((item, role))
            
    return flat_list

def build_request_approval_chain(req):
    """
    Generates and attaches the dynamic approval chain for a given request.
    Returns True if successful, False if no approvers could be resolved.
    """
    raw_approvers = get_approvers_for_request(req)
    final_approvers = flatten_approvers(raw_approvers)
    
    # REQUIREMENT 2: Exclude requester so creator NEVER appears as an approver in their own workflow
    filtered_approvers = [
        (appr, role) for (appr, role) in final_approvers
        if appr and getattr(appr, 'id', None) != req.requester_id
    ]

    if not filtered_approvers:
        admin_user = resolve_admin()
        if admin_user and getattr(admin_user, 'id', None) != req.requester_id:
            filtered_approvers = [(admin_user, "ADMIN")]

    if not filtered_approvers:
        return False

    for order, (approver, role) in enumerate(filtered_approvers, start=1):
        req.add_approval_step(approver_id=approver.id, approval_role=role, order=order)
        
    return True

def get_approvers_for_request(req):
    """
    Returns the appropriate chain of approvers based on request type.
    Format: [(resolver(), "APPROVAL_ROLE"), ...]
    """
    if req.request_type == RequestType.BUDGET_REQUEST:
        return [
            (resolve_club_faculty(req.reference_id), "CLUB_FACULTY"),
            (resolve_finance_committee(), "FINANCE_COMMITTEE"), 
            (resolve_dean_student_affairs(), "DEAN"),
            (resolve_principal(), "PRINCIPAL"),
            (resolve_admin(), "ADMIN")
        ]
        
    if req.request_type == RequestType.VENUE_REQUEST:
        return [(resolve_admin(), "ADMIN")]

    if req.request_type == RequestType.BECOME_FACULTY_COORDINATOR:
        club_id = req.reference_id
        club_faculty = resolve_club_faculty(club_id) if club_id else None
        if club_faculty and getattr(club_faculty, 'id', None) != req.requester_id:
            return [(club_faculty, "CLUB_FACULTY"), (resolve_principal(), "PRINCIPAL"), (resolve_admin(), "ADMIN")]
        return [(resolve_principal(), "PRINCIPAL"), (resolve_admin(), "ADMIN")]

    if req.request_type in {RequestType.BECOME_ORGANIZER, RequestType.BECOME_VOLUNTEER, RequestType.EDIT_CLUB_AS_COORDINATOR, RequestType.CREATE_EVENT_AS_ORGANIZER, RequestType.EDIT_EVENT_AS_ORGANIZER}:
        club_id = req.reference_id
        if req.reference_type == "EVENT" and req.reference_id:
            from app.models.events import Event
            evt = Event.query.get(req.reference_id)
            if evt and evt.club_id:
                club_id = evt.club_id
            elif evt and evt.created_by:
                creator = User.query.get(evt.created_by)
                if creator and creator.id != req.requester_id:
                    return [(creator, "EVENT_ORGANIZER")]

        club_faculty = resolve_club_faculty(club_id) if club_id else None
        if club_faculty:
            fac_id = getattr(club_faculty, 'id', None)
            if fac_id and fac_id == req.requester_id:
                return [(resolve_principal(), "PRINCIPAL"), (resolve_admin(), "ADMIN")]
            return [(club_faculty, "CLUB_FACULTY")]
        return [(resolve_principal(), "PRINCIPAL"), (resolve_admin(), "ADMIN")]

    # Default fallback
    return [(resolve_admin(), "ADMIN")]

def get_user_role(user):
    return user.role.name.upper()

def validate_request_permission(user, request_type, reference_id=None, reference_type=None):
    role = get_user_role(user)

    if request_type in {RequestType.BECOME_ORGANIZER, RequestType.BECOME_VOLUNTEER}:
        if role != "STUDENT":
            return False

        club_id = None
        if reference_type == "EVENT" and reference_id:
            from app.models.events import Event
            evt = Event.query.get(reference_id)
            if evt and evt.club_id:
                club_id = evt.club_id
        elif reference_type == "CLUB" and reference_id:
            club_id = reference_id
        elif reference_id:
            club_id = reference_id

        if club_id:
            from app.models.club import Club
            target_club = Club.query.get(club_id)
            if not target_club or target_club.club_status != 'ACTIVE':
                return False
        return True

    if request_type == RequestType.BECOME_FACULTY_COORDINATOR:
        return role == "FACULTY"

    if request_type == RequestType.EDIT_CLUB_AS_COORDINATOR:
        return ClubFaculty.query.filter_by(faculty_id=user.id, club_id=reference_id, faculty_role="FACULTY_COORDINATOR").first() is not None

    if request_type == RequestType.VENUE_REQUEST:
        if role == "ADMIN":
            return True
        if reference_type == "EVENT" and reference_id:
            from app.models.events import Event
            from app.routes.events import _can_manage_event
            evt = Event.query.get(reference_id)
            if evt:
                return _can_manage_event(evt, user)
        if reference_type == "CLUB" and reference_id:
            return ClubFaculty.query.filter_by(faculty_id=user.id, club_id=reference_id).first() is not None or ClubOrganizer.query.filter_by(user_id=user.id, club_id=reference_id).first() is not None
        return False

    if request_type in {RequestType.CREATE_EVENT_AS_ORGANIZER, RequestType.EDIT_EVENT_AS_ORGANIZER, RequestType.BUDGET_REQUEST, RequestType.SCHEDULE_REQUEST}:
        if role == "FACULTY":
            return ClubFaculty.query.filter_by(faculty_id=user.id, club_id=reference_id).first() is not None
        
        # Student organizer check: Must be an active member or organizer of the club
        if role == "STUDENT" and reference_id:
            from app.models.club import ClubMembership
            mem = ClubMembership.query.filter_by(club_id=reference_id, user_id=user.id, membership_status='ACTIVE').first()
            if not mem:
                return False
        return ClubOrganizer.query.filter_by(user_id=user.id, club_id=reference_id).first() is not None or ClubFaculty.query.filter_by(faculty_id=user.id, club_id=reference_id).first() is not None

    return False

@requests_bp.route("", methods=["POST"])
@jwt_required
def create_request():
    user = g.current_user
    legacy_err = check_legacy_user_action(user)
    if legacy_err:
        return legacy_err

    data = request.get_json() or {}

    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    request_type = data.get("requestType")
    priority = (data.get("priority") or "MEDIUM").upper()
    reference_type = data.get("referenceType")
    reference_id = data.get("referenceId")
    reference_name = data.get("referenceName")

    if not title: return jsonify({"success": False, "error": "Title is required."}), 400
    if len(title) > 150: return jsonify({"success": False, "error": "Title cannot exceed 150 characters."}), 400
    if request_type not in VALID_REQUEST_TYPES: return jsonify({"success": False, "error": "Invalid request type."}), 400
    if priority not in VALID_PRIORITIES: return jsonify({"success": False, "error": "Invalid priority."}), 400
    if reference_type not in {None, "CLUB", "EVENT"}: return jsonify({"success": False, "error": "Invalid reference type."}), 400

    if not validate_request_permission(user, request_type, reference_id, reference_type):
        return jsonify({"success": False, "error": "You are not authorized to raise this request. Club membership required."}), 403

    if reference_type == "CLUB":
        club = Club.query.get(reference_id)
        if not club: return jsonify({"success": False, "error": "Club not found."}), 404

    duplicate = Request.query.filter_by(requester_id=user.id, request_type=request_type, reference_type=reference_type, reference_id=reference_id, workflow_status=ApprovalStatus.PENDING).first()
    if duplicate:
        return jsonify({"success": False, "error": "A similar request is already pending."}), 409

    try:
        req = Request(requester_id=user.id, request_type=request_type, title=title, description=description, priority=priority, reference_type=reference_type, reference_id=reference_id, reference_name=reference_name)
        db.session.add(req)
        db.session.flush() # CRITICAL: Get req.id before attaching approvals

        custom_approvers = data.get("approvers")
        if custom_approvers and isinstance(custom_approvers, list) and len(custom_approvers) > 0:
            for order, app_info in enumerate(custom_approvers, start=1):
                appr_id = app_info.get("approverId") or app_info.get("id")
                appr_role = app_info.get("role") or "APPROVER"
                if appr_id:
                    req.add_approval_step(approver_id=int(appr_id), approval_role=appr_role, order=order)
        else:
            # Run Default Workflow Engine
            raw_approvers = get_approvers_for_request(req)
            final_approvers = flatten_approvers(raw_approvers)

            if not final_approvers:
                db.session.rollback()
                return jsonify({"success": False, "error": "Workflow error: No approvers could be resolved."}), 500

            for order, (approver, role) in enumerate(final_approvers, start=1):
                req.add_approval_step(approver_id=approver.id, approval_role=role, order=order)

        db.session.commit()
        
        # Notify approvers
        for step in RequestApproval.query.filter_by(request_id=req.id).all():
            NotificationService.create(
                user_id=step.approver_id, 
                title="New Request Assignment", 
                message=f"You have been assigned to approve request: {req.title}", 
                notification_type="TICKET",
                entity_id=req.id,
                reference_url=f"/requests/{req.id}"
            )
            
        return jsonify({"success": True, "message": "Request created successfully.", "data": req.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@requests_bp.route("", methods=["GET"])
@jwt_required
def get_requests():
    user = g.current_user
    role = get_user_role(user)

    workflow_status = request.args.get("status")
    request_type = request.args.get("type")
    priority = request.args.get("priority")
    reference_type = request.args.get("referenceType")

    query = Request.query

    if role != "ADMIN":
        query = query.filter_by(requester_id=user.id)

    if workflow_status: query = query.filter_by(workflow_status=workflow_status.upper())
    if request_type: query = query.filter_by(request_type=request_type)
    if priority: query = query.filter_by(priority=priority.upper())
    if reference_type: query = query.filter_by(reference_type=reference_type.upper())

    requests = query.order_by(Request.created_at.desc()).all()
    return jsonify({"success": True, "count": len(requests), "data": [req.to_dict() for req in requests]}), 200

@requests_bp.route("/<int:request_id>", methods=["GET"])
@jwt_required
def get_request(request_id):
    # ... (Exactly identical to your code) ...
    user = g.current_user
    role = get_user_role(user)

    req = Request.query.get(request_id)
    if not req: return jsonify({"success": False, "error": "Request not found."}), 404
    if role != "ADMIN" and req.requester_id != user.id:
        return jsonify({"success": False, "error": "You are not authorized to view this request."}), 403

    return jsonify({"success": True, "data": req.to_dict()}), 200

@requests_bp.route("/<int:request_id>", methods=["PATCH"])
@jwt_required
def update_request(request_id):
    user = g.current_user
    data = request.get_json() or {}

    req = Request.query.get(request_id)

    if not req: return jsonify({"success": False, "error": "Request not found."}), 404
    if req.requester_id != user.id: return jsonify({"success": False, "error": "You are not authorized to update this request."}), 403
    if req.workflow_status not in {ApprovalStatus.PENDING, ApprovalStatus.CHANGES_REQUESTED}:
        return jsonify({"success": False, "error": "This request can no longer be edited."}), 409

    title = (data.get("title") or req.title).strip()
    description = (data.get("description") or req.description or "").strip()
    priority = (data.get("priority") or req.priority).upper()
    reference_name = data.get("referenceName", req.reference_name)

    # Validation
    if not title: return jsonify({"success": False, "error": "Title is required."}), 400
    if len(title) > 150: return jsonify({"success": False, "error": "Title cannot exceed 150 characters."}), 400
    if priority not in VALID_PRIORITIES: return jsonify({"success": False, "error": "Invalid priority."}), 400

    try:
        req.title = title
        req.description = description
        req.priority = priority
        req.reference_name = reference_name
        
        # Wipes old approvals and bumps version
        req.resubmit() 
        db.session.flush()

        # Re-run workflow engine to attach fresh pending approvals
        raw_approvers = get_approvers_for_request(req)
        final_approvers = flatten_approvers(raw_approvers)
        
        for order, (approver, role) in enumerate(final_approvers, start=1):
            req.add_approval_step(approver_id=approver.id, approval_role=role, order=order)

        db.session.commit()
        
        # Notify approvers
        for step in RequestApproval.query.filter_by(request_id=req.id).all():
            NotificationService.create(
                user_id=step.approver_id, 
                title="Request Updated", 
                message=f"Request '{req.title}' has been updated. Please review again.", 
                notification_type="TICKET",
                entity_id=req.id,
                reference_url=f"/requests/{req.id}"
            )
            
        return jsonify({"success": True, "message": "Request updated successfully.", "data": req.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Unable to update request."}), 500

@requests_bp.route("/<int:request_id>/approve", methods=["POST"])
@jwt_required
def approve_request(request_id):
    user = g.current_user

    try:
        req = Request.query.with_for_update().filter_by(id=request_id).first() or Request.query.get(request_id)
    except Exception:
        req = Request.query.get(request_id)

    if not req: return jsonify({"success": False, "error": "Request not found."}), 404
    if req.workflow_status != ApprovalStatus.PENDING:
        return jsonify({"success": False, "error": "This request is no longer pending."}), 409

    approval = RequestApproval.query.filter_by(request_id=req.id, approver_id=user.id, status=ApprovalStatus.PENDING).first()
    if not approval:
        return jsonify({"success": False, "error": "You are not authorized to approve this request."}), 403

    try:
        approval.status = ApprovalStatus.APPROVED
        approval.approved_at = datetime.utcnow()

        remaining = RequestApproval.query.filter_by(request_id=req.id, status=ApprovalStatus.PENDING).count()

        if remaining == 0:
            req.workflow_status = ApprovalStatus.APPROVED 

            if req.is_assignment_type():
                role_str = req.request_type.replace("BECOME_", "")
                ticket = AssignmentTicket(
                    request_id=req.id, 
                    holder_id=req.requester_id, 
                    assignment_role=role_str,
                    reference_type=req.reference_type,
                    reference_id=req.reference_id,
                    duration_type=AssignmentDuration.INDEFINITE,
                    status=AssignmentStatus.ACTIVE,
                    granted_by_id=user.id
                )
                db.session.add(ticket)

                # Reflect live assignment changes directly in Club tables
                if req.reference_id:
                    if role_str in {"ORGANIZER", "PRESIDENT"}:
                        org = ClubOrganizer.query.filter_by(club_id=req.reference_id, user_id=req.requester_id).first()
                        if not org:
                            db.session.add(ClubOrganizer(club_id=req.reference_id, user_id=req.requester_id, organizer_role="ORGANIZER"))
                        from app.models.club import ClubMembership
                        mem = ClubMembership.query.filter_by(club_id=req.reference_id, user_id=req.requester_id).first()
                        if not mem:
                            db.session.add(ClubMembership(club_id=req.reference_id, user_id=req.requester_id, membership_role="ORGANIZER", membership_status="ACTIVE"))
                        else:
                            mem.membership_status = "ACTIVE"
                            mem.membership_role = "ORGANIZER"
                    elif role_str == "FACULTY_COORDINATOR":
                        fac = ClubFaculty.query.filter_by(club_id=req.reference_id, faculty_id=req.requester_id).first()
                        if not fac:
                            db.session.add(ClubFaculty(club_id=req.reference_id, faculty_id=req.requester_id, faculty_role="FACULTY_COORDINATOR"))
                    elif role_str == "VOLUNTEER":
                        from app.models.events import EventVolunteer
                        vol = EventVolunteer.query.filter_by(request_id=req.id).first()
                        if not vol and req.reference_type == "EVENT":
                            vol = EventVolunteer.query.filter_by(event_id=req.reference_id, user_id=req.requester_id).first()
                        if vol:
                            vol.volunteer_status = "ACTIVE"
                        if req.reference_type == "CLUB":
                            from app.models.club import ClubMembership
                            mem = ClubMembership.query.filter_by(club_id=req.reference_id, user_id=req.requester_id).first()
                            if not mem:
                                db.session.add(ClubMembership(club_id=req.reference_id, user_id=req.requester_id, membership_role="VOLUNTEER", membership_status="ACTIVE"))
                            else:
                                mem.membership_status = "ACTIVE"

            elif req.request_type == RequestType.CREATE_EVENT_AS_ORGANIZER:
                import json
                from app.models.events import Event
                try:
                    payload = json.loads(req.description)
                    event_name = payload.get('name')
                    if event_name:
                        start_date = datetime.strptime(payload['startDate'], '%Y-%m-%d').date()
                        end_date = datetime.strptime(payload['endDate'], '%Y-%m-%d').date()
                        start_time = datetime.strptime(payload['startTime'], '%H:%M:%S').time() if payload.get('startTime') else None
                        end_time = datetime.strptime(payload['endTime'], '%H:%M:%S').time() if payload.get('endTime') else None

                        org_type = payload.get('organizerType') or ('GENERAL' if not payload.get('clubId') else 'CLUB')
                        event = Event(
                            club_id=payload.get('clubId'),
                            venue_id=payload.get('venueId'),
                            created_by=req.requester_id,
                            organizer_type=org_type,
                            event_name=event_name,
                            event_description=payload.get('description'),
                            event_status=payload.get('status', 'SCHEDULED'),
                            start_date=start_date,
                            end_date=end_date,
                            start_time=start_time,
                            end_time=end_time,
                            capacity=payload.get('capacity', 0)
                        )
                        db.session.add(event)
                except Exception as err:
                    print("Error creating event upon request approval:", err)

            elif req.request_type == RequestType.VENUE_REQUEST:
                import json
                from app.models.events import Event, Venue
                from app.routes.events import _parse_date, _parse_time
                try:
                    payload = json.loads(req.description) if req.description and req.description.startswith('{') else {}
                    target_event_id = req.reference_id if req.reference_type == 'EVENT' else payload.get('eventId')
                    target_venue_id = payload.get('venueId')

                    if target_event_id and target_venue_id:
                        evt = Event.query.get(target_event_id)
                        target_v = Venue.query.get(target_venue_id)

                        if evt and target_v:
                            req_date = _parse_date(payload.get('date')) or evt.start_date
                            req_start = _parse_time(payload.get('startTime')) or evt.start_time
                            req_end = _parse_time(payload.get('endTime')) or evt.end_time

                            overlap_q = Event.query.filter(
                                Event.id != evt.id,
                                Event.venue_id == target_v.id,
                                Event.start_date <= (evt.end_date or req_date),
                                Event.end_date >= req_date
                            )
                            if req_start and req_end:
                                overlap_q = overlap_q.filter(
                                    Event.start_time < req_end,
                                    Event.end_time > req_start
                                )
                            conflict = overlap_q.first()

                            if conflict:
                                db.session.rollback()
                                return jsonify({
                                    "success": False,
                                    "error": f"Venue is no longer available for this time slot (Conflicting Event: '{conflict.event_name}')."
                                }), 400

                            evt.venue_id = target_v.id
                            evt.reservation_status = "RESERVED"
                            if req_start: evt.start_time = req_start
                            if req_end: evt.end_time = req_end
                except Exception as err:
                    print("Error assigning venue on request approval:", err)

        db.session.commit()
        
        NotificationService.notify_ticket_approved(
            creator_id=req.requester_id,
            ticket_id=req.id,
            approver_name=user.email
        )
        
        return jsonify({"success": True, "message": "Request approved successfully.", "data": req.to_dict()}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Unable to approve request."}), 500

@requests_bp.route("/<int:request_id>/reject", methods=["POST"])
@jwt_required
def reject_request(request_id):
    user = g.current_user
    data = request.get_json() or {}

    try:
        req = Request.query.with_for_update().filter_by(id=request_id).first() or Request.query.get(request_id)
    except Exception:
        req = Request.query.get(request_id)

    if not req: return jsonify({"success": False, "error": "Request not found."}), 404
    if req.workflow_status != ApprovalStatus.PENDING:
        return jsonify({"success": False, "error": "This request is no longer pending."}), 409

    approval = RequestApproval.query.filter_by(request_id=req.id, approver_id=user.id, status=ApprovalStatus.PENDING).first()
    if not approval:
        return jsonify({"success": False, "error": "You are not authorized to reject this request."}), 403

    try:
        approval.status = ApprovalStatus.REJECTED
        approval.remarks = data.get("comments")
        approval.approved_at = datetime.utcnow()
        req.workflow_status = ApprovalStatus.REJECTED

        db.session.commit()
        
        NotificationService.notify_ticket_rejected(
            creator_id=req.requester_id,
            ticket_id=req.id,
            approver_name=user.email
        )
        
        return jsonify({"success": True, "message": "Request rejected successfully.", "data": req.to_dict()}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Unable to reject request."}), 500
    
@requests_bp.route("/<int:request_id>/request-changes", methods=["POST"])
@jwt_required
def request_changes(request_id):
    user = g.current_user
    data = request.get_json() or {}

    try:
        req = Request.query.with_for_update().filter_by(id=request_id).first() or Request.query.get(request_id)
    except Exception:
        req = Request.query.get(request_id)

    if not req: return jsonify({"success": False, "error": "Request not found."}), 404
    if req.workflow_status != ApprovalStatus.PENDING:
        return jsonify({"success": False, "error": "This request is no longer pending."}), 409

    approval = RequestApproval.query.filter_by(request_id=req.id, approver_id=user.id, status=ApprovalStatus.PENDING).first()
    if not approval:
        return jsonify({"success": False, "error": "You are not authorized to request changes."}), 403

    try:
        approval.status = ApprovalStatus.CHANGES_REQUESTED
        approval.remarks = data.get("comments")
        approval.approved_at = datetime.utcnow()

        req.workflow_status = ApprovalStatus.CHANGES_REQUESTED

        db.session.commit()
        
        NotificationService.create(
            user_id=req.requester_id,
            title="Changes Requested",
            message=f"Changes have been requested on your request '{req.title}'.",
            notification_type="TICKET",
            entity_id=req.id,
            reference_url=f"/requests/{req.id}"
        )
        
        return jsonify({"success": True, "message": "Changes requested successfully.", "data": req.to_dict()}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "error": "Unable to request changes."}), 500

@requests_bp.route("/<int:request_id>/approvals", methods=["GET"])
@jwt_required
def get_request_approvals(request_id):
    user = g.current_user
    role = get_user_role(user)

    req = Request.query.get(request_id)
    if not req: return jsonify({"success": False, "error": "Request not found."}), 404
    if role != "ADMIN" and req.requester_id != user.id:
        return jsonify({"success": False, "error": "You are not authorized to view this request."}), 403

    approvals = RequestApproval.query.filter_by(request_id=req.id).order_by(RequestApproval.approval_order).all()
    return jsonify({"success": True, "count": len(approvals), "data": [approval.to_dict() for approval in approvals]}), 200

@requests_bp.route("/<int:request_id>/resubmit", methods=["POST"])
@jwt_required
def resubmit_request(request_id):
    user = g.current_user
    req = Request.query.get(request_id)
    if not req: return jsonify({"success": False, "error": "Request not found."}), 404
    if req.requester_id != user.id:
        return jsonify({"success": False, "error": "Only the requester can resubmit."}), 403

    data = request.get_json() or {}
    if data.get("title"): req.title = data.get("title").strip()
    if data.get("description") is not None: req.description = data.get("description").strip()
    if data.get("priority"): req.priority = data.get("priority").upper()

    try:
        req.resubmit()
        custom_approvers = data.get("approvers")
        if custom_approvers and isinstance(custom_approvers, list) and len(custom_approvers) > 0:
            for order, app_info in enumerate(custom_approvers, start=1):
                appr_id = app_info.get("approverId") or app_info.get("id")
                appr_role = app_info.get("role") or "APPROVER"
                if appr_id:
                    req.add_approval_step(approver_id=int(appr_id), approval_role=appr_role, order=order)
        else:
            if not build_request_approval_chain(req):
                db.session.rollback()
                return jsonify({"success": False, "error": "Workflow error: Could not rebuild approver chain."}), 500

        db.session.commit()
        
        # Notify approvers
        for step in RequestApproval.query.filter_by(request_id=req.id).all():
            NotificationService.create(
                user_id=step.approver_id, 
                title="Request Resubmitted", 
                message=f"Request '{req.title}' has been resubmitted for your approval.", 
                notification_type="TICKET",
                entity_id=req.id,
                reference_url=f"/requests/{req.id}"
            )
            
        return jsonify({"success": True, "message": f"Request resubmitted successfully (Version v{req.version}).", "data": req.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Resubmit failed: {str(e)}"}), 500