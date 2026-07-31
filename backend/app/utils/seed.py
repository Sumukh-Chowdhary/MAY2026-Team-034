from datetime import datetime, timedelta
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

from .seed_data import (
    ADMIN_DATA,
    FACULTY_DATA,
    STUDENT_DATA,
    CLUB_DATA
)

def seed_database():
    app = create_app()
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

        created_clubs = []
        for club in CLUB_DATA:
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
            created_clubs.append(new_club)

            fac_user = faculty_lookup[club["faculty"]]
            db.session.add(
                ClubFaculty(
                    club_id=new_club.id,
                    faculty_id=fac_user.id,
                    faculty_role="FACULTY_COORDINATOR"
                )
            )

            organizer = student_lookup[club["organizer"]]
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

        db.session.flush()

        print("6. Seeding Requests & Action Tickets & Assignment Tickets...")
        student_1 = student_users[0] # Aarav (stu1)
        student_2 = student_users[1] # Ananya (stu2)
        student_3 = student_users[2] # Rahul (stu3)
        student_4 = student_users[3] # Priya (stu4)
        student_5 = student_users[4] # Karthik (stu5)
        faculty_1 = faculty_users[0] # Dr. Meena (fac1)
        faculty_2 = faculty_users[1] # Prof. Rajesh (fac2)

        # -------------------------------------------------------------------
        # 1. Requests (Workflow Requests)
        # -------------------------------------------------------------------

        # Req 1: PENDING Multi-step Budget Request
        req1 = Request(
            requester_id=student_1.id,
            request_type=RequestType.BUDGET_REQUEST,
            title="Annual Tech Exhibition Equipment Budget",
            description="Requesting budget approval of ₹25,000 for purchasing microcontrollers, sensors, and OLED displays for Coding Club exhibition.",
            reference_type="CLUB",
            reference_id=created_clubs[0].id,
            reference_name=created_clubs[0].club_name,
            priority="HIGH",
            workflow_status=ApprovalStatus.PENDING,
            version=1
        )
        db.session.add(req1)
        db.session.flush()

        db.session.add(RequestApproval(
            request_id=req1.id, approver_id=faculty_1.id, approval_order=1,
            approval_role="CLUB_FACULTY", status=ApprovalStatus.APPROVED,
            remarks="Approved at club level. Essential hardware for student workshop.",
            approved_at=datetime.utcnow() - timedelta(days=2)
        ))
        db.session.add(RequestApproval(
            request_id=req1.id, approver_id=principal_user.id, approval_order=2,
            approval_role="PRINCIPAL", status=ApprovalStatus.PENDING,
            remarks="Reviewing allocation against semester budget."
        ))
        db.session.add(RequestApproval(
            request_id=req1.id, approver_id=user_admin.id, approval_order=3,
            approval_role="ADMIN", status=ApprovalStatus.PENDING
        ))

        # Req 2: PENDING Venue Request
        req2 = Request(
            requester_id=student_2.id,
            request_type=RequestType.VENUE_REQUEST,
            title="Main Auditorium Booking for Photo Gallery",
            description="Need Main Auditorium on 15th August for Photography Club annual exhibition gallery.",
            reference_type="CLUB",
            reference_id=created_clubs[2].id,
            reference_name=created_clubs[2].club_name,
            priority="MEDIUM",
            workflow_status=ApprovalStatus.PENDING,
            version=1
        )
        db.session.add(req2)
        db.session.flush()

        db.session.add(RequestApproval(
            request_id=req2.id, approver_id=faculty_users[2].id, approval_order=1,
            approval_role="CLUB_FACULTY", status=ApprovalStatus.PENDING,
            remarks="Awaiting venue schedule confirmation from Dean of Student Affairs."
        ))

        # Req 3: APPROVED & CLOSED Event Request
        req3 = Request(
            requester_id=student_3.id,
            request_type=RequestType.CREATE_EVENT_AS_ORGANIZER,
            title="National Inter-College Robotics Challenge 2026",
            description="Hosting 2-day national level bot combat and autonomous maze solver competition.",
            reference_type="CLUB",
            reference_id=created_clubs[1].id,
            reference_name=created_clubs[1].club_name,
            priority="HIGH",
            workflow_status=ApprovalStatus.APPROVED,
            version=1
        )
        db.session.add(req3)
        db.session.flush()

        db.session.add(RequestApproval(
            request_id=req3.id, approver_id=faculty_2.id, approval_order=1,
            approval_role="CLUB_FACULTY", status=ApprovalStatus.APPROVED,
            remarks="Great proposal. Recommended enthusiastically.",
            approved_at=datetime.utcnow() - timedelta(days=5)
        ))
        db.session.add(RequestApproval(
            request_id=req3.id, approver_id=principal_user.id, approval_order=2,
            approval_role="PRINCIPAL", status=ApprovalStatus.APPROVED,
            remarks="Approved. Ensure campus security guidelines are followed.",
            approved_at=datetime.utcnow() - timedelta(days=4)
        ))
        db.session.add(RequestApproval(
            request_id=req3.id, approver_id=user_admin.id, approval_order=3,
            approval_role="ADMIN", status=ApprovalStatus.APPROVED,
            remarks="Event scheduled and venue locked in system.",
            approved_at=datetime.utcnow() - timedelta(days=3)
        ))

        # Req 4: REJECTED Request
        req4 = Request(
            requester_id=student_1.id,
            request_type=RequestType.BUDGET_REQUEST,
            title="Vip Guest Catering & Hospitality Grant",
            description="Requesting ₹40,000 extra budget for luxury hotel stay and catering for visiting keynote speakers.",
            reference_type="CLUB",
            reference_id=created_clubs[0].id,
            reference_name=created_clubs[0].club_name,
            priority="LOW",
            workflow_status=ApprovalStatus.REJECTED,
            version=1
        )
        db.session.add(req4)
        db.session.flush()

        db.session.add(RequestApproval(
            request_id=req4.id, approver_id=faculty_1.id, approval_order=1,
            approval_role="CLUB_FACULTY", status=ApprovalStatus.APPROVED,
            remarks="Forwarding for executive review.",
            approved_at=datetime.utcnow() - timedelta(days=10)
        ))
        db.session.add(RequestApproval(
            request_id=req4.id, approver_id=principal_user.id, approval_order=2,
            approval_role="PRINCIPAL", status=ApprovalStatus.REJECTED,
            remarks="Rejected. Hospitality expenses exceed allowable student activity limit for Q3.",
            approved_at=datetime.utcnow() - timedelta(days=8)
        ))

        # Req 5: CHANGES REQUESTED Request
        req5 = Request(
            requester_id=student_2.id,
            request_type=RequestType.SCHEDULE_REQUEST,
            title="Night Astronomy Observation Camp Schedule",
            description="Schedule approval for overnight rooftop telescope stargazing session.",
            reference_type="CLUB",
            reference_id=created_clubs[2].id,
            reference_name=created_clubs[2].club_name,
            priority="MEDIUM",
            workflow_status=ApprovalStatus.CHANGES_REQUESTED,
            version=1
        )
        db.session.add(req5)
        db.session.flush()

        db.session.add(RequestApproval(
            request_id=req5.id, approver_id=faculty_users[2].id, approval_order=1,
            approval_role="CLUB_FACULTY", status=ApprovalStatus.CHANGES_REQUESTED,
            remarks="Please submit written safety protocols and list of faculty chaperones before approval.",
            approved_at=datetime.utcnow() - timedelta(days=1)
        ))

        # Action 4: Faculty Raised General Event Request
        act4 = ActionTicket(
            raised_by_id=faculty_1.id,
            ticket_type=ActionTicketType.CREATE_EVENT_GENERAL,
            title="University Annual Hackathon 2026",
            description="36-hour inter-departmental hackathon for all university students.",
            priority="HIGH",
            approval_status=ApprovalStatus.PENDING,
            version=1
        )
        db.session.add(act4)
        db.session.flush()

        db.session.add(ActionTicketApproval(
            action_ticket_id=act4.id, approver_id=principal_user.id, approval_order=1,
            approval_role="PRINCIPAL", status=ApprovalStatus.PENDING,
            remarks="Reviewing proposed dates against mid-semester examination timetable."
        ))

        # -------------------------------------------------------------------
        # 2. Action Tickets (Administrative Action Proposals)
        # -------------------------------------------------------------------

        # Action 1: PENDING Proposal (New Club)
        act1 = ActionTicket(
            raised_by_id=faculty_1.id,
            ticket_type=ActionTicketType.CREATE_CLUB,
            title="Proposal: AI & Quantum Computing Research Club",
            description="Establishment of a student research club focused on Quantum Algorithms and LLM fine-tuning.",
            priority="HIGH",
            approval_status=ApprovalStatus.PENDING,
            version=1
        )
        db.session.add(act1)
        db.session.flush()

        db.session.add(ActionTicketApproval(
            action_ticket_id=act1.id, approver_id=principal_user.id, approval_order=1,
            approval_role="PRINCIPAL", status=ApprovalStatus.APPROVED,
            remarks="Great initiative! Recommended for university registration.",
            approved_at=datetime.utcnow() - timedelta(days=1)
        ))
        db.session.add(ActionTicketApproval(
            action_ticket_id=act1.id, approver_id=user_admin.id, approval_order=2,
            approval_role="ADMIN", status=ApprovalStatus.PENDING
        ))

        # Action 2: CHANGES_REQUESTED Action Ticket
        act2 = ActionTicket(
            raised_by_id=student_3.id,
            ticket_type=ActionTicketType.CREATE_CLUB,
            title="Proposal: Esports & Game Development Society",
            description="Creating a competitive esports and game design student chapter.",
            priority="MEDIUM",
            approval_status=ApprovalStatus.CHANGES_REQUESTED,
            version=1
        )
        db.session.add(act2)
        db.session.flush()

        db.session.add(ActionTicketApproval(
            action_ticket_id=act2.id, approver_id=principal_user.id, approval_order=1,
            approval_role="PRINCIPAL", status=ApprovalStatus.APPROVED,
            remarks="Concept looks interesting.",
            approved_at=datetime.utcnow() - timedelta(days=4)
        ))
        db.session.add(ActionTicketApproval(
            action_ticket_id=act2.id, approver_id=user_admin.id, approval_order=2,
            approval_role="ADMIN", status=ApprovalStatus.CHANGES_REQUESTED,
            remarks="Please attach written consent from a faculty advisor willing to mentor the club.",
            approved_at=datetime.utcnow() - timedelta(days=2)
        ))

        # Action 3: COMPLETED Action Ticket
        act3 = ActionTicket(
            raised_by_id=faculty_2.id,
            ticket_type=ActionTicketType.CREATE_CLUB,
            title="Proposal: Autonomous Robotics Chapter",
            description="Formal establishment of Robotics Club chapter.",
            priority="HIGH",
            approval_status=ApprovalStatus.APPROVED,
            task_status="COMPLETED",
            closed_at=datetime.utcnow() - timedelta(days=15),
            version=1
        )
        db.session.add(act3)
        db.session.flush()

        db.session.add(ActionTicketApproval(
            action_ticket_id=act3.id, approver_id=principal_user.id, approval_order=1,
            approval_role="PRINCIPAL", status=ApprovalStatus.APPROVED,
            approved_at=datetime.utcnow() - timedelta(days=20)
        ))
        db.session.add(ActionTicketApproval(
            action_ticket_id=act3.id, approver_id=user_admin.id, approval_order=2,
            approval_role="ADMIN", status=ApprovalStatus.APPROVED,
            approved_at=datetime.utcnow() - timedelta(days=15)
        ))

        # -------------------------------------------------------------------
        # 3. Assignment Tickets (Live Role Grants)
        # -------------------------------------------------------------------

        # Assign 1: ACTIVE Indefinite Organizer
        assign1 = AssignmentTicket(
            request_id=req1.id,
            holder_id=student_1.id,
            assignment_role=AssignmentRole.ORGANIZER,
            reference_type="CLUB",
            reference_id=created_clubs[0].id,
            duration_type=AssignmentDuration.INDEFINITE,
            status=AssignmentStatus.ACTIVE,
            granted_by_id=user_admin.id,
            granted_at=datetime.utcnow() - timedelta(days=30)
        )

        # Assign 2: ACTIVE Date-Range Volunteer
        assign2 = AssignmentTicket(
            request_id=req2.id,
            holder_id=student_2.id,
            assignment_role=AssignmentRole.VOLUNTEER,
            reference_type="CLUB",
            reference_id=created_clubs[2].id,
            duration_type=AssignmentDuration.DATE_RANGE,
            starts_at=datetime.utcnow(),
            ends_at=datetime.utcnow() + timedelta(days=60),
            status=AssignmentStatus.ACTIVE,
            granted_by_id=user_admin.id,
            granted_at=datetime.utcnow() - timedelta(days=5)
        )

        # Assign 3: ACTIVE Faculty Coordinator
        assign3 = AssignmentTicket(
            request_id=req1.id,
            holder_id=faculty_1.id,
            assignment_role=AssignmentRole.FACULTY_COORDINATOR,
            reference_type="CLUB",
            reference_id=created_clubs[0].id,
            duration_type=AssignmentDuration.INDEFINITE,
            status=AssignmentStatus.ACTIVE,
            granted_by_id=user_admin.id,
            granted_at=datetime.utcnow() - timedelta(days=90)
        )

        # Assign 4: SUSPENDED Assignment
        assign4 = AssignmentTicket(
            request_id=req3.id,
            holder_id=student_3.id,
            assignment_role=AssignmentRole.ORGANIZER,
            reference_type="CLUB",
            reference_id=created_clubs[1].id,
            duration_type=AssignmentDuration.INDEFINITE,
            status=AssignmentStatus.SUSPENDED,
            granted_by_id=user_admin.id,
            granted_at=datetime.utcnow() - timedelta(days=40)
        )

        # Assign 5: TERMINATED Assignment
        assign5 = AssignmentTicket(
            request_id=req4.id,
            holder_id=student_4.id,
            assignment_role=AssignmentRole.VOLUNTEER,
            reference_type="CLUB",
            reference_id=created_clubs[0].id,
            duration_type=AssignmentDuration.DATE_RANGE,
            starts_at=datetime.utcnow() - timedelta(days=60),
            ends_at=datetime.utcnow() + timedelta(days=30),
            status=AssignmentStatus.TERMINATED,
            granted_by_id=user_admin.id,
            granted_at=datetime.utcnow() - timedelta(days=60)
        )

        # Assign 6: EXPIRED Assignment
        assign6 = AssignmentTicket(
            request_id=req5.id,
            holder_id=student_5.id,
            assignment_role=AssignmentRole.VOLUNTEER,
            reference_type="CLUB",
            reference_id=created_clubs[2].id,
            duration_type=AssignmentDuration.DATE_RANGE,
            starts_at=datetime.utcnow() - timedelta(days=90),
            ends_at=datetime.utcnow() - timedelta(days=10),
            status=AssignmentStatus.EXPIRED,
            granted_by_id=user_admin.id,
            granted_at=datetime.utcnow() - timedelta(days=90)
        )

        db.session.add_all([assign1, assign2, assign3, assign4, assign5, assign6])
        db.session.commit()

        print("Database successfully seeded with ALL request, ticket, and assignment possibilities!")

if __name__ == '__main__':
    seed_database()