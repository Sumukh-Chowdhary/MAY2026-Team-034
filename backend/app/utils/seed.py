from datetime import datetime, timedelta
import os
import sys
from datetime import datetime

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app import create_app
from app.models.user import (
    db, Role, Department, User, StudentProfile, FacultyProfile
)
from app.models.club import (
    Club, ClubFaculty, ClubMembership, ClubOrganizer
)
from app.models.tickets import (
    Request, RequestApproval, RequestType,
    ActionTicket, ActionTicketApproval, ActionTicketType,
    AssignmentTicket, AssignmentRole, AssignmentDuration, AssignmentStatus,
    ApprovalStatus, TaskStatus
)

from app.models.events import (
    Venue, Event, EventScheduleItem, EventAnnouncement,
    EventRegistration, EventAttendance, EventPrize, EventOrganizer, EventVolunteer
)

from app.utils.seed_data import (
    ADMIN_DATA,
    FACULTY_DATA,
    STUDENT_DATA,
    CLUB_DATA,
    VENUE_DATA,
    EVENT_DATA,
    MEMBERSHIP_SEED_DATA,
    REQUEST_SEED_DATA,
    ACTION_TICKET_SEED_DATA,
    ASSIGNMENT_TICKET_SEED_DATA
)

def seed_database(app):
    with app.app_context():
        print("Re-creating all tables...")
        db.drop_all()
        db.create_all()

        print("1. Seeding Roles...")
        role_admin = Role(name="ADMIN", description="Platform Administrator")
        role_faculty = Role(name="FACULTY", description="Faculty Advisor & Reviewer")
        role_student = Role(name="STUDENT", description="Student Member / Lead")
        db.session.add_all([role_admin, role_faculty, role_student])
        db.session.flush()

        print("2. Seeding Departments...")
        dept_admin = Department(name="Administration", code="ADM")
        dept_cs = Department(name="Computer Science", code="CSE")
        dept_ece = Department(name="Electronics", code="ECE")
        db.session.add_all([dept_admin, dept_cs, dept_ece])
        db.session.flush()

        department_map = {
            dept.code: dept.id
            for dept in [dept_admin, dept_cs, dept_ece]
        }

        print("3. Seeding Users...")
        user_admin = User(
            email=ADMIN_DATA["email"],
            role_id=role_admin.id,
            account_status="ACTIVE"
        )
        user_admin.set_password(ADMIN_DATA["password"])

        faculty_users = []
        principal_user = None

        for faculty in FACULTY_DATA:
            user = User(
                email=faculty["email"],
                role_id=role_faculty.id,
                account_status="ACTIVE"
            )
            user.set_password(faculty["password"])
            faculty_users.append(user)
            if faculty.get("designation") == "PRINCIPAL":
                principal_user = user

        student_users = []
        for student in STUDENT_DATA:
            user = User(
                email=student["email"],
                role_id=role_student.id,
                account_status="ACTIVE"
            )
            user.set_password(student["password"])
            student_users.append(user)

        db.session.add_all([user_admin, *faculty_users, *student_users])
        db.session.flush()

        print("4. Seeding Profiles...")
        admin_profile = StudentProfile(
            user_id=user_admin.id,
            roll_no=ADMIN_DATA["roll_no"],
            full_name=ADMIN_DATA["full_name"],
            phone_number=ADMIN_DATA["phone_number"],
            year_of_study=ADMIN_DATA["year_of_study"],
            department_id=department_map[ADMIN_DATA["department"]],
            bio=ADMIN_DATA["bio"]
        )
        db.session.add(admin_profile)

        for user, faculty in zip(faculty_users, FACULTY_DATA):
            profile = FacultyProfile(
                user_id=user.id,
                employee_id=faculty["employee_id"],
                full_name=faculty["full_name"],
                phone_number=faculty["phone_number"],
                designation=faculty["designation"],
                department_id=department_map[faculty["department"]],
                bio=faculty["bio"]
            )
            db.session.add(profile)

        for user, student in zip(student_users, STUDENT_DATA):
            profile = StudentProfile(
                user_id=user.id,
                roll_no=student["roll_no"],
                full_name=student["full_name"],
                phone_number=student["phone_number"],
                year_of_study=student["year_of_study"],
                department_id=department_map[student["department"]],
                bio=student["bio"]
            )
            db.session.add(profile)

        db.session.flush()

        print("5. Seeding Clubs...")
        faculty_lookup = {
            faculty["employee_id"]: user
            for faculty, user in zip(FACULTY_DATA, faculty_users)
        }

        student_lookup = {
            student["roll_no"]: user
            for student, user in zip(STUDENT_DATA, student_users)
        }

        club_lookup = {}

        club_lookup = {}

        for club in CLUB_DATA:
            if "category" not in club or "faculty" not in club:
                continue
            new_club = Club(
                club_name=club["name"],
                club_description=club["description"],
                club_category=club["category"],
                club_logo=club["logo"],
                club_status="ACTIVE",
                total_members=1,
                active_members=1
            )
            db.session.add(new_club)
            db.session.flush()
            club_lookup[new_club.club_name] = new_club

            fac_user = faculty_lookup[club["faculty"]]
            db.session.add(
                ClubFaculty(
                    club_id=new_club.id,
                    faculty_id=fac_user.id,
                    faculty_role="FACULTY_COORDINATOR"
                )
            )

            organizer = student_lookup.get(club["organizer"]) or student_users[0]
            db.session.add(
                ClubOrganizer(
                    club_id=new_club.id,
                    user_id=organizer.id,
                    organizer_role="PRESIDENT"
                )
            )

            db.session.add(
                ClubMembership(
                    club_id=new_club.id,
                    user_id=organizer.id,
                    membership_role="MEMBER",
                    membership_status="ACTIVE"
                )
            )

        print("5b. Seeding Additional Club Memberships...")
        for mem in MEMBERSHIP_SEED_DATA:
            existing = ClubMembership.query.filter_by(
                club_id=mem["club_id"],
                user_id=mem["user_id"]
            ).first()
            if not existing:
                db.session.add(
                    ClubMembership(
                        club_id=mem["club_id"],
                        user_id=mem["user_id"],
                        membership_role=mem.get("membership_role", "MEMBER"),
                        membership_status=mem.get("membership_status", "ACTIVE")
                    )
                )

        # Update member counts for every club
        for club in Club.query.all():
            total_members = ClubMembership.query.filter_by(
                club_id=club.id
            ).count()

            active_members = ClubMembership.query.filter_by(
                club_id=club.id,
                membership_status="ACTIVE"
            ).count()

            club.total_members = total_members
            club.active_members = active_members

        db.session.flush()

        print("6. Seeding Venues...")
        venue_lookup = {}

        for venue_data in VENUE_DATA:
            venue = Venue(
                venue_name=venue_data["name"],
                venue_location=venue_data["location"],
                venue_type=venue_data["type"],
                capacity=venue_data["capacity"],
                availability_status=venue_data["availabilityStatus"]
            )
            db.session.add(venue)
            db.session.flush()
            venue_lookup[venue.venue_name] = venue

        print("7. Seeding Events...")
        user_lookup = {
            user.email: user
            for user in [user_admin, *faculty_users, *student_users]
        }

        for event_data in EVENT_DATA:
            club = club_lookup.get(event_data.get("clubName"))
            creator = user_lookup.get(event_data.get("createdByEmail"))
            venue = venue_lookup.get(event_data.get("venueName"))
            org_type = event_data.get("organizerType") or ("GENERAL" if not club else "CLUB")

            if not creator:
                continue

            event = Event(
                club_id=club.id if club else None,
                created_by=creator.id,
                venue_id=venue.id if venue else None,
                organizer_type=org_type,
                event_name=event_data["name"],
                event_description=event_data["description"],
                event_status=event_data["status"],
                start_date=datetime.strptime(event_data["startDate"], "%Y-%m-%d").date(),
                end_date=datetime.strptime(event_data["endDate"], "%Y-%m-%d").date(),
                start_time=datetime.strptime(event_data["startTime"], "%H:%M:%S").time(),
                end_time=datetime.strptime(event_data["endTime"], "%H:%M:%S").time(),
                capacity=event_data["capacity"]
            )
            db.session.add(event)
            db.session.flush()

            for item in event_data.get("schedule", []):
                db.session.add(EventScheduleItem(
                    event_id=event.id,
                    schedule_time=item["time"],
                    activity=item["activity"]
                ))

            for item in event_data.get("announcements", []):
                db.session.add(EventAnnouncement(
                    event_id=event.id,
                    title=item["title"],
                    message=item["message"]
                ))

            for email in event_data.get("registrations", []):
                user = user_lookup.get(email)
                if user:
                    db.session.add(EventRegistration(
                        event_id=event.id,
                        user_id=user.id,
                        registration_status="REGISTERED"
                    ))

            for email in event_data.get("attendance", []):
                user = user_lookup.get(email)
                if user:
                    db.session.add(EventAttendance(
                        event_id=event.id,
                        user_id=user.id,
                        attendance_status="PRESENT"
                    ))

            for prize in event_data.get("prizes", []):
                winner = user_lookup.get(prize.get("winnerEmail"))
                db.session.add(EventPrize(
                    event_id=event.id,
                    title=prize["title"],
                    winner_name=winner.student_profile.full_name if winner and winner.student_profile else None,
                    description=prize.get("description")
                ))

            for email in event_data.get("organizers", []):
                user = user_lookup.get(email)
                if user:
                    db.session.add(EventOrganizer(
                        event_id=event.id,
                        user_id=user.id,
                        organizer_role="ORGANIZER"
                    ))

            for email in event_data.get("volunteers", []):
                user = user_lookup.get(email)
                if user:
                    db.session.add(EventVolunteer(
                        event_id=event.id,
                        user_id=user.id,
                        volunteer_status="PENDING"
                    ))

        print("8. Seeding Requests & Approvals...")
        event_lookup = {
            e.event_name: e
            for e in Event.query.all()
        }

        for req_data in REQUEST_SEED_DATA:
            requester = user_lookup.get(req_data["requesterEmail"])
            if not requester:
                continue

            ref_id = None
            if req_data.get("referenceType") == "CLUB":
                c = club_lookup.get(req_data.get("referenceName"))
                ref_id = c.id if c else None
            elif req_data.get("referenceType") == "EVENT":
                e = event_lookup.get(req_data.get("referenceName"))
                ref_id = e.id if e else None

            req = Request(
                requester_id=requester.id,
                request_type=req_data["requestType"],
                title=req_data["title"],
                description=req_data.get("description"),
                reference_type=req_data.get("referenceType"),
                reference_id=ref_id,
                reference_name=req_data.get("referenceName"),
                priority=req_data.get("priority", "MEDIUM"),
                workflow_status=req_data.get("workflowStatus", "PENDING")
            )
            db.session.add(req)
            db.session.flush()

            for app_data in req_data.get("approvals", []):
                approver = user_lookup.get(app_data["approverEmail"])
                if approver:
                    db.session.add(RequestApproval(
                        request_id=req.id,
                        approver_id=approver.id,
                        approval_order=app_data.get("approvalOrder", 1),
                        approval_role=app_data.get("approvalRole", "REVIEWER"),
                        status=app_data.get("status", "PENDING"),
                        remarks=app_data.get("remarks"),
                        approved_at=datetime.utcnow() if app_data.get("status") in ["APPROVED", "REJECTED", "CHANGES_REQUESTED"] else None
                    ))

        print("9. Seeding Action Tickets...")
        for ticket_data in ACTION_TICKET_SEED_DATA:
            raised_by = user_lookup.get(ticket_data["raisedByEmail"])
            assigned_to = user_lookup.get(ticket_data.get("assignedToEmail"))
            if not raised_by:
                continue

            closed_at_val = None
            if ticket_data.get("closedAt"):
                closed_at_val = datetime.fromisoformat(ticket_data["closedAt"])

            ticket = ActionTicket(
                raised_by_id=raised_by.id,
                ticket_type=ticket_data["ticketType"],
                title=ticket_data["title"],
                description=ticket_data.get("description"),
                priority=ticket_data.get("priority", "MEDIUM"),
                approval_status=ticket_data.get("approvalStatus", "PENDING"),
                assigned_to_id=assigned_to.id if assigned_to else None,
                task_status=ticket_data.get("taskStatus"),
                due_date=datetime.strptime(ticket_data["dueDate"], "%Y-%m-%d").date() if ticket_data.get("dueDate") else None,
                completion_remarks=ticket_data.get("completionRemarks"),
                closed_at=closed_at_val
            )
            db.session.add(ticket)
            db.session.flush()

            for app_data in ticket_data.get("approvals", []):
                approver = user_lookup.get(app_data["approverEmail"])
                if approver:
                    db.session.add(ActionTicketApproval(
                        action_ticket_id=ticket.id,
                        approver_id=approver.id,
                        approval_order=app_data.get("approvalOrder", 1),
                        approval_role=app_data.get("approvalRole", "REVIEWER"),
                        status=app_data.get("status", "PENDING"),
                        remarks=app_data.get("remarks"),
                        approved_at=datetime.utcnow() if app_data.get("status") in ["APPROVED", "REJECTED", "CHANGES_REQUESTED"] else None
                    ))

        print("10. Seeding Assignment Tickets...")
        for assign_data in ASSIGNMENT_TICKET_SEED_DATA:
            holder = user_lookup.get(assign_data["holderEmail"])
            granted_by = user_lookup.get(assign_data.get("grantedByEmail"))
            if not holder:
                continue

            ref_id = None
            if assign_data.get("referenceType") == "CLUB":
                c = club_lookup.get(assign_data.get("clubName"))
                ref_id = c.id if c else None
            elif assign_data.get("referenceType") == "EVENT":
                e = event_lookup.get(assign_data.get("eventName"))
                ref_id = e.id if e else None

            req_obj = Request.query.filter_by(requester_id=holder.id).first()

            starts_at_val = datetime.fromisoformat(assign_data["startsAt"]) if assign_data.get("startsAt") else datetime.utcnow()
            ends_at_val = datetime.fromisoformat(assign_data["endsAt"]) if assign_data.get("endsAt") else None

            ticket = AssignmentTicket(
                request_id=req_obj.id if req_obj else 1,
                holder_id=holder.id,
                assignment_role=assign_data["assignmentRole"],
                reference_type=assign_data.get("referenceType"),
                reference_id=ref_id,
                duration_type=assign_data.get("durationType", "INDEFINITE"),
                starts_at=starts_at_val,
                ends_at=ends_at_val,
                status=assign_data.get("status", "ACTIVE"),
                granted_by_id=granted_by.id if granted_by else None
            )
            db.session.add(ticket)

        db.session.commit()

        print("Database successfully seeded with ALL request, ticket, and assignment possibilities!")

if __name__ == '__main__':
    app = create_app()
    seed_database(app)