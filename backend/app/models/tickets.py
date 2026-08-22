from datetime import datetime
from app.models import db
from app.models.user import User, FacultyProfile
from app.models.club import ClubOrganizer, ClubFaculty

class RequestType:
    """Request types that go through the Assignment or Approval-only
    workflows (i.e. NOT Action items - those are raised as ActionTickets
    directly, see below)."""
    BECOME_ORGANIZER = "BECOME_ORGANIZER"          # -> Assignment
    BECOME_VOLUNTEER = "BECOME_VOLUNTEER"          # -> Assignment
    BECOME_FACULTY_COORDINATOR = "BECOME_FACULTY_COORDINATOR"  # -> Assignment

    CREATE_EVENT_AS_ORGANIZER = "CREATE_EVENT_AS_ORGANIZER"  # -> Approval-only
    EDIT_EVENT_AS_ORGANIZER = "EDIT_EVENT_AS_ORGANIZER"      # -> Approval-only
    EDIT_CLUB_AS_COORDINATOR = "EDIT_CLUB_AS_COORDINATOR"    # -> Approval-only
    VENUE_REQUEST = "VENUE_REQUEST"                # -> Approval-only
    BUDGET_REQUEST = "BUDGET_REQUEST"              # -> Approval-only
    SCHEDULE_REQUEST = "SCHEDULE_REQUEST"          # -> Approval-only

    # Types that result in an AssignmentTicket once fully approved.
    ASSIGNMENT_TYPES = {BECOME_ORGANIZER, BECOME_VOLUNTEER, BECOME_FACULTY_COORDINATOR}
    # Types where the requester just proceeds themselves once approved -
    # no ticket generated at all.
    APPROVAL_ONLY_TYPES = {
        CREATE_EVENT_AS_ORGANIZER, EDIT_EVENT_AS_ORGANIZER, EDIT_CLUB_AS_COORDINATOR,
        VENUE_REQUEST, BUDGET_REQUEST, SCHEDULE_REQUEST
    }

class ActionTicketType:
    """Things nobody has standing permission to do themselves - raised
    directly as a ticket, no separate Request underneath. NOTE: no delete
    types by design, deletion isn't supported anywhere in this system."""
    CREATE_CLUB = "CREATE_CLUB"
    CREATE_EVENT_GENERAL = "CREATE_EVENT_GENERAL"     # non-club event
    CREATE_EVENT_FOR_CLUB = "CREATE_EVENT_FOR_CLUB"   # club event, requester isn't the organizer
    EDIT_CLUB_ADMIN = "EDIT_CLUB_ADMIN"               # club edit, requester isn't the coordinator
    EDIT_EVENT_ADMIN = "EDIT_EVENT_ADMIN"

class AssignmentRole:
    ORGANIZER = "ORGANIZER"
    VOLUNTEER = "VOLUNTEER"
    FACULTY_COORDINATOR = "FACULTY_COORDINATOR"
    EVENT_ORGANIZER = "EVENT_ORGANIZER"   # student assigned to run a general event
    EVENT_FACULTY = "EVENT_FACULTY"       # faculty assigned to a general event

class AssignmentDuration:
    DATE_RANGE = "DATE_RANGE"
    INDEFINITE = "INDEFINITE"

class AssignmentStatus:
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    EXPIRED = "EXPIRED"

class ApprovalStatus:
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    SKIPPED = "SKIPPED"

class TaskStatus:
    """Execution status for an ActionTicket once approvals are done -
    this is the 'admin's to-do list' side of things."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


# ---------------------------------------------------------------------------
# Approver resolution - no department/HOD involved anywhere anymore.
# Four possible sources: Admin, Principal, Club Organizer (student), Club
# Faculty (faculty tied to one club).
# ---------------------------------------------------------------------------
def resolve_admin():
    """Any user with the ADMIN role. Returns the first one found -
    if you have multiple admins, any one of them approving/acting is fine."""
    return User.query.join(User.role).filter_by(name="ADMIN").first()

def resolve_principal():
    """The Principal is just a faculty account with FacultyProfile.designation
    == 'PRINCIPAL' - not tied to any club or department. Exists purely to be
    tagged as an approver (e.g. new club creation, budget approvals)."""
    profile = FacultyProfile.query.filter_by(designation="PRINCIPAL").first()
    return profile.user if profile else None

def resolve_club_organizer(club_id, organizer_role="ORGANIZER"):
    entry = ClubOrganizer.query.filter_by(club_id=club_id, organizer_role=organizer_role).first()
    if not entry:
        entry = ClubOrganizer.query.filter_by(club_id=club_id).first()
    return entry.user if entry else None

def resolve_club_faculty(club_id, faculty_role="FACULTY_COORDINATOR"):
    entry = ClubFaculty.query.filter_by(club_id=club_id, faculty_role=faculty_role).first()
    if not entry:
        entry = ClubFaculty.query.filter_by(club_id=club_id).first()
    return entry.faculty if entry else None

# ---------------------------------------------------------------------------
# Request  (Assignment workflow + Approval-only workflow)
# ---------------------------------------------------------------------------
class Request(db.Model):
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    request_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    reference_type = db.Column(db.String(50), nullable=True)   # "CLUB" / "EVENT"
    reference_id = db.Column(db.Integer, nullable=True)
    reference_name = db.Column(db.String(150), nullable=True)

    priority = db.Column(db.String(20), nullable=False, default="MEDIUM")
    workflow_status = db.Column(db.String(20), nullable=False, default=ApprovalStatus.PENDING)
    version = db.Column(db.Integer, nullable=False, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester = db.relationship("User", lazy=True)
    approvals = db.relationship(
        "RequestApproval", backref="request", lazy=True,
        cascade="all, delete-orphan", order_by="RequestApproval.approval_order"
    )
    assignment_ticket = db.relationship(
        "AssignmentTicket", backref="request", uselist=False, cascade="all, delete-orphan"
    )

    def add_approval_step(self, approver_id, approval_role, order):
        """approver_id is resolved by the caller (via resolve_admin /
        resolve_principal / resolve_club_organizer / resolve_club_faculty)
        BEFORE calling this, since resolution depends on which club/event
        this request is about."""
        step = RequestApproval(
            request_id=self.id, approver_id=approver_id,
            approval_order=order, approval_role=approval_role,
            status=ApprovalStatus.PENDING,
        )
        db.session.add(step)
        return step

    def resubmit(self):
        """Edit & resubmit: wipe approvals, bump version. Caller re-adds
        approval steps afterward."""
        for approval in list(self.approvals):
            db.session.delete(approval)
        self.version += 1
        self.workflow_status = ApprovalStatus.PENDING
        self.updated_at = datetime.utcnow()

    def all_approved(self):
        return bool(self.approvals) and all(a.status == ApprovalStatus.APPROVED for a in self.approvals)

    def is_assignment_type(self):
        return self.request_type in RequestType.ASSIGNMENT_TYPES

    def to_dict(self):
        return {
            "id": self.id,
            "requesterId": self.requester_id,
            "requestType": self.request_type,
            "title": self.title,
            "description": self.description,
            "referenceType": self.reference_type,
            "referenceId": self.reference_id,
            "referenceName": self.reference_name,
            "priority": self.priority,
            "workflowStatus": self.workflow_status,
            "version": self.version,
            "approvals": [a.to_dict() for a in self.approvals],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

class RequestApproval(db.Model):
    __tablename__ = "request_approvals"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    approval_order = db.Column(db.Integer, nullable=False, default=1)
    approval_role = db.Column(db.String(50), nullable=False)  # "ADMIN" / "PRINCIPAL" / "CLUB_ORGANIZER" / "CLUB_FACULTY"
    status = db.Column(db.String(20), default=ApprovalStatus.PENDING)
    remarks = db.Column(db.Text)
    approved_at = db.Column(db.DateTime)

    approver = db.relationship("User", lazy=True)

    def get_approver_dict(self):
        if not self.approver:
            return None
        
        role_name = self.approver.role.name.upper() if (self.approver and self.approver.role) else "USER"
        email = self.approver.email
        name = email.split('@')[0]
        desig = self.approval_role.replace('_', ' ').title()

        if role_name == "ADMIN":
            name = "Admin User"
            desig = "Administrator"
        elif self.approver.faculty_profile:
            name = self.approver.faculty_profile.full_name
            desig = self.approver.faculty_profile.designation or "Faculty Advisor"
        elif self.approver.student_profile:
            name = self.approver.student_profile.full_name
            desig = "Student"

        return {
            "id": self.approver.id,
            "name": name,
            "email": email,
            "designation": desig
        }

    def to_dict(self):
        return {
            "id": self.id,
            "approverId": self.approver_id,
            "approvalOrder": self.approval_order,
            "approvalRole": self.approval_role,
            "status": self.status,
            "remarks": self.remarks,
            "approvedAt": self.approved_at.isoformat() if self.approved_at else None,
            "approver": self.get_approver_dict()
        }


# ---------------------------------------------------------------------------
# AssignmentTicket  (role grants - unchanged in shape from before)
# ---------------------------------------------------------------------------
class AssignmentTicket(db.Model):
    __tablename__ = "assignment_tickets"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("requests.id"), nullable=False)
    holder_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    assignment_role = db.Column(db.String(50), nullable=False)  # AssignmentRole.*
    reference_type = db.Column(db.String(50))  # "CLUB" / "EVENT"
    reference_id = db.Column(db.Integer)

    duration_type = db.Column(db.String(20), nullable=False, default=AssignmentDuration.INDEFINITE)
    starts_at = db.Column(db.DateTime, default=datetime.utcnow)
    ends_at = db.Column(db.DateTime, nullable=True)  # null for INDEFINITE

    status = db.Column(db.String(20), nullable=False, default=AssignmentStatus.ACTIVE)

    granted_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    holder = db.relationship("User", foreign_keys=[holder_id], lazy=True)
    granted_by = db.relationship("User", foreign_keys=[granted_by_id], lazy=True)

    # --- Admin-editable lifecycle, per "admin can edit indefinite -> date range etc" ---

    def suspend(self, performed_by_id, remarks=None):
        self.status = AssignmentStatus.SUSPENDED
        log_action("ASSIGNMENT_TICKET", self.id, performed_by_id, "Assignment Suspended", remarks)

    def reactivate(self, performed_by_id, remarks=None):
        self.status = AssignmentStatus.ACTIVE
        log_action("ASSIGNMENT_TICKET", self.id, performed_by_id, "Assignment Reactivated", remarks)

    def terminate(self, performed_by_id, remarks=None):
        self.status = AssignmentStatus.TERMINATED
        log_action("ASSIGNMENT_TICKET", self.id, performed_by_id, "Assignment Terminated", remarks)

    def edit_duration(self, performed_by_id, duration_type, ends_at=None, remarks=None):
        """e.g. admin converts an INDEFINITE grant to a DATE_RANGE one."""
        self.duration_type = duration_type
        self.ends_at = ends_at
        log_action(
            "ASSIGNMENT_TICKET", self.id, performed_by_id,
            "Assignment Duration Edited", remarks or f"Changed to {duration_type}"
        )

    def check_expiry(self):
        if (self.duration_type == AssignmentDuration.DATE_RANGE and self.ends_at
                and self.ends_at < datetime.utcnow() and self.status == AssignmentStatus.ACTIVE):
            self.status = AssignmentStatus.EXPIRED

    @classmethod
    def current_for(cls, user_id):
        """Student's LIVE permissions."""
        return cls.query.filter_by(holder_id=user_id, status=AssignmentStatus.ACTIVE).all()

    @classmethod
    def history_for(cls, user_id):
        """Student's permission history (past/inactive grants)."""
        return cls.query.filter(
            cls.holder_id == user_id, cls.status != AssignmentStatus.ACTIVE
        ).all()

    def get_holder_dict(self):
        if not self.holder:
            return None
        name = self.holder.email.split('@')[0]
        if self.holder.student_profile:
            name = self.holder.student_profile.full_name
        elif self.holder.faculty_profile:
            name = self.holder.faculty_profile.full_name
        return {
            "id": self.holder.id,
            "name": name,
            "email": self.holder.email
        }

    def get_reference_name(self):
        if self.reference_type == "CLUB" and self.reference_id:
            from app.models.club import Club
            c = Club.query.get(self.reference_id)
            return c.club_name if c else f"Club #{self.reference_id}"
        return f"#{self.reference_id}"

    def to_dict(self):
        return {
            "id": self.id,
            "requestId": self.request_id,
            "holderId": self.holder_id,
            "holder": self.get_holder_dict(),
            "assignmentRole": self.assignment_role,
            "referenceType": self.reference_type,
            "referenceId": self.reference_id,
            "referenceName": self.get_reference_name(),
            "durationType": self.duration_type,
            "startsAt": self.starts_at.isoformat() if self.starts_at else None,
            "endsAt": self.ends_at.isoformat() if self.ends_at else None,
            "status": self.status,
            "grantedById": self.granted_by_id,
            "grantedAt": self.granted_at.isoformat() if self.granted_at else None,
        }


# ---------------------------------------------------------------------------
# ActionTicket  (merged Request + Ticket, per your call above)
# ---------------------------------------------------------------------------
class ActionTicket(db.Model):
    """Raised directly by whoever has the idea (student or faculty) - no
    separate Request underneath. Carries its own approval chain AND the
    execution/task fields for whoever ends up doing the work."""
    __tablename__ = "action_tickets"

    id = db.Column(db.Integer, primary_key=True)
    raised_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ticket_type = db.Column(db.String(50), nullable=False)  # ActionTicketType.*
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    reference_type = db.Column(db.String(50), nullable=True)   # null for brand-new club/event that doesn't exist yet
    reference_id = db.Column(db.Integer, nullable=True)
    reference_name = db.Column(db.String(150), nullable=True)

    priority = db.Column(db.String(20), nullable=False, default="MEDIUM")
    version = db.Column(db.Integer, nullable=False, default=1)

    # Approval phase
    approval_status = db.Column(db.String(20), nullable=False, default=ApprovalStatus.PENDING)

    # Execution phase - only meaningful once approval_status == APPROVED
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    task_status = db.Column(db.String(20), nullable=True)  # TaskStatus.*
    due_date = db.Column(db.Date, nullable=True)
    completion_remarks = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    raised_by = db.relationship("User", foreign_keys=[raised_by_id], lazy=True)
    assigned_to = db.relationship("User", foreign_keys=[assigned_to_id], lazy=True)
    approvals = db.relationship(
        "ActionTicketApproval", backref="action_ticket", lazy=True,
        cascade="all, delete-orphan", order_by="ActionTicketApproval.approval_order"
    )

    def add_approval_step(self, approver_id, approval_role, order):
        step = ActionTicketApproval(
            action_ticket_id=self.id, approver_id=approver_id,
            approval_order=order, approval_role=approval_role,
            status=ApprovalStatus.PENDING,
        )
        db.session.add(step)
        return step

    def all_approved(self):
        return bool(self.approvals) and all(a.status == ApprovalStatus.APPROVED for a in self.approvals)

    def mark_approved_and_open_task(self, assigned_to_id):
        """Call once all_approved() - opens the execution/task side."""
        self.approval_status = ApprovalStatus.APPROVED
        self.assigned_to_id = assigned_to_id
        self.task_status = TaskStatus.OPEN

    def resubmit(self):
        """Edit & resubmit after Changes Requested - resets approvals only,
        task fields untouched since they haven't started yet at that point."""
        for approval in list(self.approvals):
            db.session.delete(approval)
        self.version += 1
        self.approval_status = ApprovalStatus.PENDING
        self.updated_at = datetime.utcnow()

    def start_task(self, performed_by_id):
        self.task_status = TaskStatus.IN_PROGRESS
        log_action("ACTION_TICKET", self.id, performed_by_id, "Task In Progress")

    def complete_task(self, performed_by_id, remarks=None):
        self.task_status = TaskStatus.COMPLETED
        self.completion_remarks = remarks
        self.closed_at = datetime.utcnow()
        log_action("ACTION_TICKET", self.id, performed_by_id, "Ticket Closed", remarks)

    @classmethod
    def current(cls):
        """Admin view: still open (not yet closed)."""
        return cls.query.filter(cls.closed_at.is_(None)).all()

    @classmethod
    def old(cls):
        return cls.query.filter(cls.closed_at.isnot(None)).all()

    @classmethod
    def tagged_for_faculty(cls, user_id):
        """Faculty view: tickets where they're an approver OR the assignee."""
        approver_ticket_ids = db.session.query(ActionTicketApproval.action_ticket_id).filter_by(
            approver_id=user_id
        )
        return cls.query.filter(
            db.or_(cls.assigned_to_id == user_id, cls.id.in_(approver_ticket_ids))
        ).all()

    def to_dict(self):
        return {
            "id": self.id,
            "raisedById": self.raised_by_id,
            "ticketType": self.ticket_type,
            "title": self.title,
            "description": self.description,
            "referenceType": self.reference_type,
            "referenceId": self.reference_id,
            "referenceName": self.reference_name,
            "priority": self.priority,
            "version": self.version,
            "approvalStatus": self.approval_status,
            "assignedToId": self.assigned_to_id,
            "taskStatus": self.task_status,
            "dueDate": self.due_date.isoformat() if self.due_date else None,
            "completionRemarks": self.completion_remarks,
            "approvals": [a.to_dict() for a in self.approvals],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "closedAt": self.closed_at.isoformat() if self.closed_at else None,
        }


class ActionTicketApproval(db.Model):
    __tablename__ = "action_ticket_approvals"

    id = db.Column(db.Integer, primary_key=True)
    action_ticket_id = db.Column(db.Integer, db.ForeignKey("action_tickets.id"), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    approval_order = db.Column(db.Integer, nullable=False, default=1)
    approval_role = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default=ApprovalStatus.PENDING)
    remarks = db.Column(db.Text)
    approved_at = db.Column(db.DateTime)

    approver = db.relationship("User", lazy=True)

    def get_approver_dict(self):
        if not self.approver:
            return None
        
        role_name = self.approver.role.name.upper() if (self.approver and self.approver.role) else "USER"
        email = self.approver.email
        name = email.split('@')[0]
        desig = self.approval_role.replace('_', ' ').title()

        if role_name == "ADMIN":
            name = "Admin User"
            desig = "Administrator"
        elif self.approver.faculty_profile:
            name = self.approver.faculty_profile.full_name
            desig = self.approver.faculty_profile.designation or "Faculty Advisor"
        elif self.approver.student_profile:
            name = self.approver.student_profile.full_name
            desig = "Student"

        return {
            "id": self.approver.id,
            "name": name,
            "email": email,
            "designation": desig
        }

    def to_dict(self):
        return {
            "id": self.id,
            "approverId": self.approver_id,
            "approvalOrder": self.approval_order,
            "approvalRole": self.approval_role,
            "status": self.status,
            "remarks": self.remarks,
            "approvedAt": self.approved_at.isoformat() if self.approved_at else None,
            "approver": self.get_approver_dict()
        }


# ---------------------------------------------------------------------------
# TicketAudit  (shared by both ticket kinds via subject_type/subject_id)
# ---------------------------------------------------------------------------

class TicketAudit(db.Model):
    __tablename__ = "ticket_audit"

    id = db.Column(db.Integer, primary_key=True)
    subject_type = db.Column(db.String(20), nullable=False)  # "ACTION_TICKET" / "ASSIGNMENT_TICKET"
    subject_id = db.Column(db.Integer, nullable=False)
    performed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "subjectType": self.subject_type,
            "subjectId": self.subject_id,
            "performedBy": self.performed_by,
            "action": self.action,
            "remarks": self.remarks,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

def log_action(subject_type, subject_id, performed_by_id, action, remarks=None):
    db.session.add(TicketAudit(
        subject_type=subject_type, subject_id=subject_id,
        performed_by=performed_by_id, action=action, remarks=remarks,
    ))