from datetime import datetime, date, time, timedelta
import os
import sys
import json
import random

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
    ApprovalStatus, TaskStatus, TicketAudit, log_action
)
from app.models.events import (
    Venue, Event, EventScheduleItem, EventAnnouncement,
    EventRegistration, EventAttendance, EventPrize, EventOrganizer, EventVolunteer,
    EventSession, ParticipantRoundStatus
)
from app.models.notification import Notification

from app.utils.seed_data import (
    DEPARTMENTS_DATA,
    ADMIN_DATA_LIST,
    PRINCIPAL_DATA,
    FACULTY_DATA_LIST,
    STUDENT_DATA_LIST,
    CLUB_DATA_LIST,
    VENUE_DATA_LIST
)

random.seed(42)

def seed_database(app=None):
    if app is None:
        app = create_app()

    with app.app_context():
        print("1. Dropping and Re-creating Database Schema...")
        db.drop_all()
        db.create_all()

        print("2. Seeding System Roles...")
        role_admin = Role(name="ADMIN", description="Platform Administrator with full system control")
        role_faculty = Role(name="FACULTY", description="Faculty Advisor, Coordinator & Reviewer")
        role_student = Role(name="STUDENT", description="Student Member, Volunteer & Event Lead")
        db.session.add_all([role_admin, role_faculty, role_student])
        db.session.flush()

        role_map = {
            "ADMIN": role_admin.id,
            "FACULTY": role_faculty.id,
            "STUDENT": role_student.id
        }

        print("3. Seeding Departments...")
        dept_lookup = {}
        for d_info in DEPARTMENTS_DATA:
            dept = Department(name=d_info["name"], code=d_info["code"])
            db.session.add(dept)
            db.session.flush()
            dept_lookup[d_info["code"]] = dept.id

        print("4. Seeding Admin Users & Profiles...")
        admin_users = []
        for a_data in ADMIN_DATA_LIST:
            u_admin = User(
                email=a_data["email"],
                role_id=role_map["ADMIN"],
                account_status="ACTIVE"
            )
            u_admin.set_password(a_data["password"])
            db.session.add(u_admin)
            db.session.flush()
            
            p_admin = StudentProfile(
                user_id=u_admin.id,
                roll_no=a_data["roll_no"],
                full_name=a_data["full_name"],
                phone_number=a_data["phone_number"],
                year_of_study=None,
                department_id=dept_lookup[a_data["department"]],
                bio=a_data["bio"]
            )
            db.session.add(p_admin)
            admin_users.append(u_admin)

        print("5. Seeding Faculty Users & Profiles...")
        faculty_users = []
        faculty_map_by_empid = {}

        for f_data in FACULTY_DATA_LIST:
            u_fac = User(
                email=f_data["email"],
                role_id=role_map["FACULTY"],
                account_status="ACTIVE"
            )
            u_fac.set_password(f_data["password"])
            db.session.add(u_fac)
            db.session.flush()

            p_fac = FacultyProfile(
                user_id=u_fac.id,
                employee_id=f_data["employee_id"],
                full_name=f_data["full_name"],
                phone_number=f_data["phone_number"],
                designation=f_data["designation"],
                department_id=dept_lookup[f_data["department"]],
                bio=f_data["bio"]
            )
            db.session.add(p_fac)
            faculty_users.append(u_fac)
            faculty_map_by_empid[f_data["employee_id"]] = u_fac

        print("6. Seeding Student Users & Profiles...")
        student_users = []
        student_map_by_roll = {}

        from app.utils.registration_id import parse_registration_id, get_branch_code

        for s_data in STUDENT_DATA_LIST:
            u_stu = User(
                email=s_data["email"],
                role_id=role_map["STUDENT"],
                account_status=s_data.get("account_status", "ACTIVE")
            )
            u_stu.set_password(s_data["password"])
            db.session.add(u_stu)
            db.session.flush()

            parsed = parse_registration_id(s_data["roll_no"])
            batch_yr = (int(parsed["batchYear"]) + 2000) if parsed else 2026
            br_code = parsed["branchCode"] if parsed else get_branch_code(s_data["department"])
            roll_num = int(parsed["rollNumber"]) if parsed else u_stu.id
            grad_yr = batch_yr + 4

            p_stu = StudentProfile(
                user_id=u_stu.id,
                roll_no=s_data["roll_no"],
                registration_id=s_data["roll_no"],
                batch_year=batch_yr,
                branch_code=br_code,
                roll_number=roll_num,
                graduation_year=grad_yr,
                full_name=s_data["full_name"],
                phone_number=s_data["phone_number"],
                year_of_study=s_data["year_of_study"],
                department_id=dept_lookup[s_data["department"]],
                bio=s_data["bio"]
            )
            db.session.add(p_stu)
            student_users.append(u_stu)
            student_map_by_roll[s_data["roll_no"]] = u_stu

        db.session.flush()

        print("7. Seeding Clubs, Coordinators, Organizers, and Memberships...")
        clubs_list = []
        club_map_by_name = {}

        for c_data in CLUB_DATA_LIST:
            club = Club(
                club_name=c_data["name"],
                club_category=c_data["category"],
                club_description=c_data["description"],
                club_logo=c_data["logo"],
                club_status="ACTIVE",
                total_members=0,
                active_members=0
            )
            db.session.add(club)
            db.session.flush()
            clubs_list.append(club)
            club_map_by_name[club.club_name] = club

            # Faculty coordinator
            fac_user = faculty_map_by_empid.get(c_data["faculty_emp_id"]) or faculty_users[0]
            db.session.add(ClubFaculty(
                club_id=club.id,
                faculty_id=fac_user.id,
                faculty_role="FACULTY_COORDINATOR"
            ))

            # Student Organizer / President
            org_user = student_map_by_roll.get(c_data["organizer_roll_no"]) or student_users[0]
            db.session.add(ClubOrganizer(
                club_id=club.id,
                user_id=org_user.id,
                organizer_role="PRESIDENT"
            ))

            # Add President as active member
            db.session.add(ClubMembership(
                club_id=club.id,
                user_id=org_user.id,
                membership_role="ORGANIZER",
                membership_status="ACTIVE"
            ))

        db.session.flush()

        # Seed realistic club memberships across 100 students
        print("7b. Distributing Student Memberships across Clubs...")
        for s_idx, stu in enumerate(student_users):
            # Each student joins 1 to 4 clubs deterministically
            num_clubs = 1 + (s_idx % 4)
            chosen_clubs = random.sample(clubs_list, num_clubs)
            for club in chosen_clubs:
                existing = ClubMembership.query.filter_by(club_id=club.id, user_id=stu.id).first()
                if not existing:
                    is_leg = (stu.account_status == "LEGACY" or getattr(stu, 'is_legacy', False))
                    m_role = "VOLUNTEER" if (s_idx % 7 == 0) else "MEMBER"
                    m_status = "INACTIVE" if is_leg else ("ACTIVE" if (s_idx % 12 != 0) else "INACTIVE")
                    end_dt = (datetime.utcnow() - timedelta(days=120)) if is_leg else None
                    db.session.add(ClubMembership(
                        club_id=club.id,
                        user_id=stu.id,
                        membership_role=m_role,
                        membership_status=m_status,
                        ended_at=end_dt
                    ))

        db.session.flush()

        # Update member counts for all clubs
        for club in clubs_list:
            club.total_members = ClubMembership.query.filter_by(club_id=club.id).count()
            club.active_members = ClubMembership.query.filter_by(club_id=club.id, membership_status="ACTIVE").count()

        db.session.flush()

        print("8. Seeding Venues...")
        venues_list = []
        venue_map_by_name = {}
        for v_data in VENUE_DATA_LIST:
            v = Venue(
                venue_name=v_data["name"],
                venue_location=v_data["location"],
                venue_type=v_data["type"],
                capacity=v_data["capacity"],
                availability_status=v_data["availabilityStatus"]
            )
            db.session.add(v)
            db.session.flush()
            venues_list.append(v)
            venue_map_by_name[v.venue_name] = v

        print("9. Seeding Events, Sessions, Competitions, Registrations & Attendance...")
        
        # Event Specs List (50 events total)
        # Dates relative to current date 2026-08-11:
        # Completed: 2026-06-01 to 2026-08-05
        # Live: 2026-08-07 to 2026-08-14
        # Scheduled: 2026-08-20 to 2026-11-30

        EVENT_SPECS = [
            # INSTITUTIONAL / GENERAL EVENTS (club_id = None)
            {
                "name": "Freshers Orientation 2026",
                "organizerType": "GENERAL", "clubName": None,
                "createdBy": faculty_users[0].id,
                "description": "Annual welcoming orientation ceremony for first-year undergraduate students.",
                "status": "COMPLETED", "format": "SEMINAR",
                "startDate": date(2026, 7, 15), "endDate": date(2026, 7, 15),
                "startTime": time(9, 30), "endTime": time(16, 30),
                "capacity": 500, "venueName": "Main Auditorium",
                "rounds": []
            },
            {
                "name": "Independence Day Celebration 2026",
                "organizerType": "GENERAL", "clubName": None,
                "createdBy": faculty_users[0].id,
                "description": "Institutional flag hoisting ceremony, cultural parade, and patriotic speeches.",
                "status": "SCHEDULED", "format": "CULTURAL",
                "startDate": date(2026, 8, 15), "endDate": date(2026, 8, 15),
                "startTime": time(8, 0), "endTime": time(12, 0),
                "capacity": 800, "venueName": "Open Air Ground",
                "rounds": []
            },
            {
                "name": "Annual Cultural Fest — Rhythm 2026",
                "organizerType": "GENERAL", "clubName": None,
                "createdBy": faculty_users[1].id,
                "description": "Inter-college 3-day cultural festival with music, dance, drama, and art galas.",
                "status": "SCHEDULED", "format": "FESTIVAL",
                "startDate": date(2026, 9, 20), "endDate": date(2026, 9, 22),
                "startTime": time(10, 0), "endTime": time(21, 0),
                "capacity": 800, "venueName": "Open Air Theatre",
                "rounds": []
            },
            {
                "name": "Graduation Ceremony 2026",
                "organizerType": "GENERAL", "clubName": None,
                "createdBy": faculty_users[2].id,
                "description": "Official convocation ceremony for graduating seniors and postgraduate scholars.",
                "status": "COMPLETED", "format": "CEREMONY",
                "startDate": date(2026, 6, 30), "endDate": date(2026, 6, 30),
                "startTime": time(10, 0), "endTime": time(13, 0),
                "capacity": 400, "venueName": "Main Auditorium",
                "rounds": []
            },
            {
                "name": "Campus Career & Placement Fair",
                "organizerType": "GENERAL", "clubName": None,
                "createdBy": faculty_users[8].id, # Dr. Ramesh Babu
                "description": "Placement drive bringing top engineering and management recruiters to campus.",
                "status": "SCHEDULED", "format": "EXPO",
                "startDate": date(2026, 10, 10), "endDate": date(2026, 10, 11),
                "startTime": time(9, 0), "endTime": time(18, 0),
                "capacity": 600, "venueName": "Conference Hall Alpha",
                "rounds": []
            },
            {
                "name": "Annual Research & Innovation Symposium",
                "organizerType": "GENERAL", "clubName": None,
                "createdBy": faculty_users[7].id, # Dr. Vikramaditya Sen
                "description": "Paper presentations, poster sessions, and keynote talks on emerging technologies.",
                "status": "COMPLETED", "format": "SYMPOSIUM",
                "startDate": date(2026, 7, 28), "endDate": date(2026, 7, 28),
                "startTime": time(9, 0), "endTime": time(17, 0),
                "capacity": 200, "venueName": "Conference Hall Alpha",
                "rounds": []
            },
            {
                "name": "Annual Sports Meet 2026",
                "organizerType": "GENERAL", "clubName": None,
                "createdBy": faculty_users[1].id,
                "description": "Inter-department athletics, football, cricket, and indoor sports championship.",
                "status": "SCHEDULED", "format": "COMPETITION",
                "startDate": date(2026, 11, 5), "endDate": date(2026, 11, 7),
                "startTime": time(7, 30), "endTime": time(18, 0),
                "capacity": 800, "venueName": "Sports Complex Ground",
                "rounds": []
            },

            # CLUB COMPETITIONS & WORKSHOPS
            # 1. AI Club
            {
                "name": "AI Hack Sprint 2026",
                "organizerType": "CLUB", "clubName": "AI Club",
                "createdBy": faculty_users[0].id,
                "description": "24-hour hackathon to build state-of-the-art AI prototypes and machine learning solutions.",
                "status": "LIVE", "format": "COMPETITION",
                "startDate": date(2026, 8, 7), "endDate": date(2026, 8, 12),
                "startTime": time(9, 0), "endTime": time(17, 0),
                "capacity": 80, "venueName": "Innovation Lab",
                "rounds": ["Round 1 — Preliminary Pitch", "Round 2 — Technical Evaluation", "Round 3 — Grand Final Demos"]
            },
            {
                "name": "Machine Learning Fundamentals Workshop",
                "organizerType": "CLUB", "clubName": "AI Club",
                "createdBy": faculty_users[0].id,
                "description": "Hands-on workshop covering regression, classification, PyTorch models, and evaluation metrics.",
                "status": "COMPLETED", "format": "WORKSHOP",
                "startDate": date(2026, 7, 10), "endDate": date(2026, 7, 10),
                "startTime": time(10, 0), "endTime": time(16, 0),
                "capacity": 60, "venueName": "Computer Center Lab 1",
                "rounds": []
            },

            # 2. Coding Club
            {
                "name": "Competitive Coding Championship",
                "organizerType": "CLUB", "clubName": "Coding Club",
                "createdBy": student_users[0].id,
                "description": "Multi-stage algorithmic programming contest featuring dynamic programming and graph theory.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 7, 20), "endDate": date(2026, 7, 21),
                "startTime": time(14, 0), "endTime": time(18, 0),
                "capacity": 100, "venueName": "Computer Center Lab 1",
                "rounds": ["Round 1 — Online Qualifier", "Round 2 — Speed Programming", "Round 3 — Hardcore Finals"]
            },
            {
                "name": "Open Source Sprint 2026",
                "organizerType": "CLUB", "clubName": "Coding Club",
                "createdBy": student_users[0].id,
                "description": "Collaborative sprint contributing to active GitHub repositories and developer tools.",
                "status": "LIVE", "format": "COMPETITION",
                "startDate": date(2026, 8, 10), "endDate": date(2026, 8, 13),
                "startTime": time(10, 0), "endTime": time(17, 0),
                "capacity": 70, "venueName": "Innovation Lab",
                "rounds": ["Round 1 — Bug Bounty Sprint", "Round 2 — Feature PR Submissions"]
            },

            # 3. Robotics Club
            {
                "name": "RoboWars & Autonomous Bot Challenge",
                "organizerType": "CLUB", "clubName": "Robotics Club",
                "createdBy": faculty_users[1].id, # Dr. Arjun Nair
                "description": "Hardware combat and autonomous line-follower obstacle navigation challenge.",
                "status": "LIVE", "format": "COMPETITION",
                "startDate": date(2026, 8, 9), "endDate": date(2026, 8, 14),
                "startTime": time(10, 0), "endTime": time(16, 0),
                "capacity": 50, "venueName": "Robotics Lab",
                "rounds": ["Round 1 — Hardware Inspection", "Round 2 — Obstacle Trial", "Round 3 — Arena Battle"]
            },

            # 4. Photography Club
            {
                "name": "Monsoon Photo Walk 2026",
                "organizerType": "CLUB", "clubName": "Photography Club",
                "createdBy": student_users[5].id, # Meera Das
                "description": "Guided outdoor photography walk exploring macro and portrait shots across campus.",
                "status": "COMPLETED", "format": "WORKSHOP",
                "startDate": date(2026, 7, 25), "endDate": date(2026, 7, 25),
                "startTime": time(7, 0), "endTime": time(11, 0),
                "capacity": 40, "venueName": "Open Air Ground",
                "rounds": []
            },

            # 5. Drama Club
            {
                "name": "Stagecraft Annual Play Auditions & Finale",
                "organizerType": "CLUB", "clubName": "Drama Club",
                "createdBy": student_users[3].id, # Sneha Nair
                "description": "Full-length theatrical drama production followed by monologue competition.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 7, 18), "endDate": date(2026, 7, 19),
                "startTime": time(15, 0), "endTime": time(20, 0),
                "capacity": 120, "venueName": "Studio Hall",
                "rounds": ["Round 1 — Audition Monologues", "Round 2 — Final Stage Play"]
            },

            # 6. Music Club
            {
                "name": "Battle of the Bands 2026",
                "organizerType": "CLUB", "clubName": "Music Club",
                "createdBy": student_users[6].id,
                "description": "Inter-department band face-off featuring rock, fusion, and acoustic sets.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 7, 22), "endDate": date(2026, 7, 23),
                "startTime": time(17, 0), "endTime": time(21, 30),
                "capacity": 350, "venueName": "Open Air Theatre",
                "rounds": ["Round 1 — Acoustic Prelims", "Round 2 — Amplified Semi Finals", "Round 3 — Grand Finale"]
            },

            # 7. Debate Club
            {
                "name": "All-India Parliamentary Debate Tournament",
                "organizerType": "CLUB", "clubName": "Debate Club",
                "createdBy": student_users[7].id,
                "description": "Asian Parliamentary format debate competition discussing global economic policy and AI ethics.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 6, 25), "endDate": date(2026, 6, 27),
                "startTime": time(9, 0), "endTime": time(18, 0),
                "capacity": 100, "venueName": "Seminar Room 101",
                "rounds": ["Round 1 — Preliminary Motion", "Round 2 — Quarter Finals", "Round 3 — Semi Finals", "Round 4 — Grand Final"]
            },

            # 8. Entrepreneurship Club
            {
                "name": "E-Summit Startup Pitch Fest",
                "organizerType": "CLUB", "clubName": "Entrepreneurship Club",
                "createdBy": faculty_users[8].id,
                "description": "Student startup pitch competition before angel investors and industry leaders.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 7, 5), "endDate": date(2026, 7, 6),
                "startTime": time(10, 0), "endTime": time(17, 0),
                "capacity": 150, "venueName": "Conference Hall Alpha",
                "rounds": ["Round 1 — Executive Summary Pitch", "Round 2 — Prototype Demo", "Round 3 — Investor Q&A Final"]
            },

            # 9. Cyber Security Club
            {
                "name": "Capture The Flag (CTF) Cyber Challenge",
                "organizerType": "CLUB", "clubName": "Cyber Security Club",
                "createdBy": student_users[10].id,
                "description": "Jeopardy-style CTF covering web exploitation, cryptography, reverse engineering, and forensics.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 7, 12), "endDate": date(2026, 7, 13),
                "startTime": time(10, 0), "endTime": time(18, 0),
                "capacity": 80, "venueName": "Innovation Lab",
                "rounds": ["Round 1 — Qualifier Challenges", "Round 2 — Final Exploitation Attack"]
            },

            # 10. Data Science Club
            {
                "name": "Kaggle Data Hackathon 2026",
                "organizerType": "CLUB", "clubName": "Data Science Club",
                "createdBy": faculty_users[7].id,
                "description": "Predictive modeling and feature engineering hackathon on real-world datasets.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 7, 2), "endDate": date(2026, 7, 4),
                "startTime": time(9, 30), "endTime": time(17, 30),
                "capacity": 90, "venueName": "Computer Center Lab 1",
                "rounds": ["Round 1 — Exploratory Analysis", "Round 2 — Model Optimization", "Round 3 — Leaderboard Final"]
            },

            # 11. Gaming Club
            {
                "name": "Campus Esports League 2026",
                "organizerType": "CLUB", "clubName": "Gaming Club",
                "createdBy": student_users[18].id,
                "description": "LAN tournament featuring Valorant, Rocket League, and Chess.com blitz matches.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 6, 15), "endDate": date(2026, 6, 17),
                "startTime": time(11, 0), "endTime": time(19, 0),
                "capacity": 120, "venueName": "Innovation Lab",
                "rounds": ["Round 1 — Group Stage", "Round 2 — Quarter Finals", "Round 3 — Semi Finals", "Round 4 — Grand Finals"]
            },

            # 12. Design Club
            {
                "name": "UI/UX Redesign Hackathon",
                "organizerType": "CLUB", "clubName": "Design Club",
                "createdBy": student_users[1].id, # Ananya Gupta
                "description": "Figma design sprint creating accessible mobile app interfaces.",
                "status": "COMPLETED", "format": "COMPETITION",
                "startDate": date(2026, 7, 14), "endDate": date(2026, 7, 15),
                "startTime": time(10, 0), "endTime": time(16, 0),
                "capacity": 60, "venueName": "Studio Hall",
                "rounds": ["Round 1 — Wireframing Challenge", "Round 2 — High-Fidelity Prototype Pitch"]
            },

            # UPCOMING EVENTS (SCHEDULED) FOR VARIOUS CLUBS
            {
                "name": "Deep Learning & LLM Masterclass",
                "organizerType": "CLUB", "clubName": "AI Club",
                "createdBy": faculty_users[0].id,
                "description": "Hands-on tutorial on fine-tuning Transformer models and RAG architectures.",
                "status": "SCHEDULED", "format": "WORKSHOP",
                "startDate": date(2026, 8, 25), "endDate": date(2026, 8, 25),
                "startTime": time(10, 0), "endTime": time(16, 0),
                "capacity": 80, "venueName": "Innovation Lab",
                "rounds": []
            },
            {
                "name": "Web Development Bootcamp 2026",
                "organizerType": "CLUB", "clubName": "Coding Club",
                "createdBy": student_users[0].id,
                "description": "Full-stack web application development with Vue 3, Flask, and PostgreSQL.",
                "status": "SCHEDULED", "format": "WORKSHOP",
                "startDate": date(2026, 9, 1), "endDate": date(2026, 9, 3),
                "startTime": time(14, 0), "endTime": time(17, 0),
                "capacity": 100, "venueName": "Computer Center Lab 1",
                "rounds": []
            },
            {
                "name": "Autonomous Drone Racing Challenge",
                "organizerType": "CLUB", "clubName": "Robotics Club",
                "createdBy": student_users[2].id,
                "description": "FPV drone obstacle course and autonomous flight navigation competition.",
                "status": "SCHEDULED", "format": "COMPETITION",
                "startDate": date(2026, 9, 15), "endDate": date(2026, 9, 16),
                "startTime": time(10, 0), "endTime": time(17, 0),
                "capacity": 60, "venueName": "Sports Complex Ground",
                "rounds": ["Round 1 — Time Trial", "Round 2 — Obstacle Track Finale"]
            },
            {
                "name": "Stargazing & Telescope Observation Night",
                "organizerType": "CLUB", "clubName": "Astronomy Club",
                "createdBy": student_users[12].id,
                "description": "Night observation of Saturn rings, lunar craters, and deep-space nebulae.",
                "status": "SCHEDULED", "format": "WORKSHOP",
                "startDate": date(2026, 8, 28), "endDate": date(2026, 8, 28),
                "startTime": time(19, 30), "endTime": time(23, 0),
                "capacity": 150, "venueName": "Open Air Ground",
                "rounds": []
            },
            {
                "name": "CAD Design & 3D Printing Challenge",
                "organizerType": "CLUB", "clubName": "Mechanical Innovation Club",
                "createdBy": faculty_users[4].id,
                "description": "SolidWorks 3D modeling challenge followed by rapid prototyping printing.",
                "status": "SCHEDULED", "format": "COMPETITION",
                "startDate": date(2026, 9, 10), "endDate": date(2026, 9, 11),
                "startTime": time(10, 0), "endTime": time(16, 0),
                "capacity": 50, "venueName": "Robotics Lab",
                "rounds": ["Round 1 — 3D Part Design", "Round 2 — Stress Analysis & Print"]
            },
            {
                "name": "Campus Cleanliness & E-Waste Drive",
                "organizerType": "CLUB", "clubName": "Eco Club",
                "createdBy": faculty_users[5].id,
                "description": "Campus-wide e-waste collection drive and tree sapling distribution.",
                "status": "SCHEDULED", "format": "SOCIAL",
                "startDate": date(2026, 8, 22), "endDate": date(2026, 8, 22),
                "startTime": time(8, 30), "endTime": time(13, 0),
                "capacity": 200, "venueName": "Open Air Ground",
                "rounds": []
            },
            {
                "name": "Financial Literacy & Stock Trading Workshop",
                "organizerType": "CLUB", "clubName": "Finance Club",
                "createdBy": faculty_users[16].id,
                "description": "Personal finance management, equity analysis, and mutual fund basics.",
                "status": "SCHEDULED", "format": "WORKSHOP",
                "startDate": date(2026, 9, 5), "endDate": date(2026, 9, 5),
                "startTime": time(14, 0), "endTime": time(17, 0),
                "capacity": 100, "venueName": "Seminar Room 101",
                "rounds": []
            }
        ]

        created_events_lookup = {}

        for spec in EVENT_SPECS:
            club_obj = club_map_by_name.get(spec["clubName"]) if spec["clubName"] else None
            venue_obj = venue_map_by_name.get(spec["venueName"]) if spec["venueName"] else None
            
            evt = Event(
                club_id=club_obj.id if club_obj else None,
                created_by=spec["createdBy"],
                venue_id=venue_obj.id if venue_obj else None,
                organizer_type=spec["organizerType"],
                reservation_status="RESERVED" if venue_obj else "NONE",
                event_name=spec["name"],
                event_description=spec["description"],
                event_status=spec["status"],
                start_date=spec["startDate"],
                end_date=spec["endDate"],
                start_time=spec["startTime"],
                end_time=spec["endTime"],
                capacity=spec["capacity"],
                event_format=spec["format"]
            )
            db.session.add(evt)
            db.session.flush()
            created_events_lookup[evt.event_name] = evt

            # Add Schedule Items
            db.session.add(EventScheduleItem(event_id=evt.id, schedule_time=spec["startTime"].strftime("%H:%M"), activity="Registration & Keynote Opening"))
            db.session.add(EventScheduleItem(event_id=evt.id, schedule_time="13:00", activity="Lunch & Networking Session"))
            db.session.add(EventScheduleItem(event_id=evt.id, schedule_time=spec["endTime"].strftime("%H:%M"), activity="Closing Ceremony & Feedback"))

            # Add Announcements
            db.session.add(EventAnnouncement(
                event_id=evt.id,
                title=f"Welcome to {evt.event_name}",
                message=f"We are excited to host {evt.event_name}. Please arrive on time at {venue_obj.venue_name if venue_obj else 'the designated venue'}.",
                created_by_id=spec["createdBy"],
                created_at=datetime.utcnow() - timedelta(days=2)
            ))
            if spec["status"] in ["LIVE", "COMPLETED"]:
                db.session.add(EventAnnouncement(
                    event_id=evt.id,
                    title="Important Update & Schedule Reminder",
                    message="Please check the session agenda and complete your venue check-in.",
                    created_by_id=spec["createdBy"],
                    created_at=datetime.utcnow() - timedelta(hours=5)
                ))

            # Add Organizers
            db.session.add(EventOrganizer(event_id=evt.id, user_id=spec["createdBy"], organizer_role="LEAD_ORGANIZER"))
            # Add 2 student organizers
            for org_stu in student_users[:2]:
                if org_stu.id != spec["createdBy"]:
                    db.session.add(EventOrganizer(event_id=evt.id, user_id=org_stu.id, organizer_role="COORGANIZER"))

            # Add Volunteers
            for v_idx, vol_stu in enumerate(student_users[5:15]):
                v_stat = "APPROVED" if (v_idx % 2 == 0) else "PENDING"
                db.session.add(EventVolunteer(event_id=evt.id, user_id=vol_stu.id, volunteer_status=v_stat))

            # Seed Sessions & Competition Rounds
            sessions_list = []
            if spec["rounds"]:
                for r_idx, r_name in enumerate(spec["rounds"], start=1):
                    r_stat = "COMPLETED" if spec["status"] == "COMPLETED" or (spec["status"] == "LIVE" and r_idx < len(spec["rounds"])) else ("ACTIVE" if spec["status"] == "LIVE" and r_idx == len(spec["rounds"]) else "UPCOMING")
                    sess = EventSession(
                        event_id=evt.id,
                        name=r_name,
                        round_number=r_idx,
                        status=r_stat,
                        session_date=evt.start_date + timedelta(days=r_idx - 1),
                        start_time=evt.start_time.strftime("%H:%M") if evt.start_time else "10:00",
                        end_time=evt.end_time.strftime("%H:%M") if evt.end_time else "17:00",
                        description=f"Evaluation round {r_idx} for {evt.event_name}."
                    )
                    db.session.add(sess)
                    db.session.flush()
                    sessions_list.append(sess)

            # Seed Registrations & Attendance & Progression
            # Sample 15 to 30 students to register for each event
            registered_students = random.sample(student_users, min(25, len(student_users)))
            for reg_idx, reg_stu in enumerate(registered_students):
                r_status = "ATTENDED" if spec["status"] == "COMPLETED" else ("REGISTERED" if reg_idx < 20 else "CANCELLED")
                reg = EventRegistration(
                    event_id=evt.id,
                    user_id=reg_stu.id,
                    registration_status=r_status,
                    registered_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                )
                db.session.add(reg)

                # Seed Attendance for past/live events
                if spec["status"] in ["COMPLETED", "LIVE"]:
                    att_status = "PRESENT" if (reg_idx % 5 != 0) else "ABSENT"
                    db.session.add(EventAttendance(
                        event_id=evt.id,
                        session_id=sessions_list[0].id if sessions_list else None,
                        user_id=reg_stu.id,
                        attendance_status=att_status,
                        marked_by_id=spec["createdBy"],
                        marked_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
                    ))

            db.session.flush()

            # Seed Competition Round Progression (ParticipantRoundStatus) & Prizes
            if spec["rounds"] and sessions_list:
                pool = registered_students[:18]
                for s_idx, sess in enumerate(sessions_list):
                    next_pool = []
                    for p_user in pool:
                        # Top 50% shortlisted, remainder eliminated
                        is_shortlisted = (pool.index(p_user) < max(2, len(pool) // 2))
                        p_stat = "SHORTLISTED" if is_shortlisted else "ELIMINATED"
                        if is_shortlisted:
                            next_pool.append(p_user)

                        db.session.add(ParticipantRoundStatus(
                            event_id=evt.id,
                            session_id=sess.id,
                            user_id=p_user.id,
                            status=p_stat,
                            reason=f"Round {sess.round_number} performance evaluation.",
                            updated_by_id=spec["createdBy"]
                        ))
                    pool = next_pool

                # Add Prizes if event is COMPLETED
                if spec["status"] == "COMPLETED" and len(registered_students) >= 3:
                    db.session.add(EventPrize(
                        event_id=evt.id,
                        title="Winner — 1st Place",
                        winner_name=registered_students[0].student_profile.full_name,
                        description="Awarded Cash Prize ₹10,000 & Certificate of Excellence"
                    ))
                    db.session.add(EventPrize(
                        event_id=evt.id,
                        title="Runner Up — 2nd Place",
                        winner_name=registered_students[1].student_profile.full_name,
                        description="Awarded Cash Prize ₹5,000 & Certificate of Merit"
                    ))
                    db.session.add(EventPrize(
                        event_id=evt.id,
                        title="2nd Runner Up — 3rd Place",
                        winner_name=registered_students[2].student_profile.full_name,
                        description="Awarded Cash Prize ₹2,500 & Certificate of Appreciation"
                    ))

        db.session.flush()

        print("10. Seeding Requests & Multi-level Approval Workflows...")
        # Seed 70+ Requests
        REQUEST_TYPES_LIST = [
            RequestType.BECOME_ORGANIZER,
            RequestType.BECOME_VOLUNTEER,
            RequestType.BECOME_FACULTY_COORDINATOR,
            RequestType.CREATE_EVENT_AS_ORGANIZER,
            RequestType.EDIT_EVENT_AS_ORGANIZER,
            RequestType.EDIT_CLUB_AS_COORDINATOR,
            RequestType.VENUE_REQUEST,
            RequestType.BUDGET_REQUEST,
            RequestType.SCHEDULE_REQUEST
        ]

        requests_count = 0
        for r_i in range(75):
            req_type = REQUEST_TYPES_LIST[r_i % len(REQUEST_TYPES_LIST)]
            requester = student_users[r_i % len(student_users)] if req_type not in [RequestType.BECOME_FACULTY_COORDINATOR, RequestType.EDIT_CLUB_AS_COORDINATOR] else faculty_users[r_i % len(faculty_users)]
            target_club = clubs_list[r_i % len(clubs_list)]
            target_event = list(created_events_lookup.values())[r_i % len(created_events_lookup)]

            ref_type = "EVENT" if req_type in [RequestType.VENUE_REQUEST, RequestType.EDIT_EVENT_AS_ORGANIZER, RequestType.SCHEDULE_REQUEST] else "CLUB"
            ref_id = target_event.id if ref_type == "EVENT" else target_club.id
            ref_name = target_event.event_name if ref_type == "EVENT" else target_club.club_name

            w_status = ApprovalStatus.APPROVED if (r_i % 2 == 0) else (ApprovalStatus.PENDING if (r_i % 3 == 0) else ApprovalStatus.REJECTED)

            req_desc = f"Requesting authorization for {req_type} regarding {ref_name}."
            if req_type == RequestType.VENUE_REQUEST:
                v_target = venues_list[r_i % len(venues_list)]
                req_desc = json.dumps({
                    "venueId": v_target.id,
                    "venueName": v_target.venue_name,
                    "date": "2026-08-25",
                    "startTime": "10:00 AM",
                    "endTime": "04:00 PM",
                    "reason": "Special lab equipment and auditorium setup required."
                })
            elif req_type == RequestType.BUDGET_REQUEST:
                req_desc = json.dumps({
                    "amount": 25000 + (r_i * 1000),
                    "purpose": "Prize pool money and equipment rental for upcoming hackathon.",
                    "clubId": target_club.id
                })

            req_obj = Request(
                requester_id=requester.id,
                request_type=req_type,
                title=f"{req_type.replace('_', ' ').title()} for {ref_name}",
                description=req_desc,
                reference_type=ref_type,
                reference_id=ref_id,
                reference_name=ref_name,
                priority="HIGH" if (r_i % 4 == 0) else "MEDIUM",
                workflow_status=w_status
            )
            db.session.add(req_obj)
            db.session.flush()
            requests_count += 1

            # Attach Approval steps
            # Step 1: Faculty
            step1_status = ApprovalStatus.APPROVED if w_status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED] else ApprovalStatus.PENDING
            db.session.add(RequestApproval(
                request_id=req_obj.id,
                approver_id=faculty_users[r_i % len(faculty_users)].id,
                approval_order=1,
                approval_role="FACULTY_COORDINATOR",
                status=step1_status,
                approved_at=datetime.utcnow() if step1_status == ApprovalStatus.APPROVED else None
            ))

            # Step 2: Admin
            step2_status = w_status
            db.session.add(RequestApproval(
                request_id=req_obj.id,
                approver_id=admin_users[0].id,
                approval_order=2,
                approval_role="ADMIN",
                status=step2_status,
                approved_at=datetime.utcnow() if step2_status == ApprovalStatus.APPROVED else None
            ))

        db.session.flush()

        print("11. Seeding Assignment Tickets, Action Tickets & Ticket Audit Logs...")
        # Assignment Tickets
        for t_idx, club in enumerate(clubs_list[:15]):
            holder_stu = student_users[t_idx]
            db.session.add(AssignmentTicket(
                request_id=t_idx + 1,
                holder_id=holder_stu.id,
                assignment_role=AssignmentRole.ORGANIZER,
                reference_type="CLUB",
                reference_id=club.id,
                duration_type=AssignmentDuration.INDEFINITE,
                starts_at=datetime.utcnow() - timedelta(days=60),
                status=AssignmentStatus.ACTIVE,
                granted_by_id=admin_users[0].id
            ))

        # Seed EXPIRED historical assignment tickets for explicit LEGACY students
        legacy_students_expired_roles = [
            ("Y22CS001", AssignmentRole.ORGANIZER, "AI Club"),
            ("Y22EC004", AssignmentRole.ORGANIZER, "Drama Club"),
            ("Y21ME002", AssignmentRole.VOLUNTEER, "Robotics Club"),
        ]
        for roll, a_role, c_name in legacy_students_expired_roles:
            leg_u = student_map_by_roll.get(roll)
            l_club = club_map_by_name.get(c_name)
            if leg_u and l_club:
                db.session.add(AssignmentTicket(
                    request_id=1,
                    holder_id=leg_u.id,
                    assignment_role=a_role,
                    reference_type="CLUB",
                    reference_id=l_club.id,
                    duration_type=AssignmentDuration.DATE_RANGE,
                    starts_at=datetime.utcnow() - timedelta(days=365),
                    ends_at=datetime.utcnow() - timedelta(days=60),
                    status=AssignmentStatus.EXPIRED,
                    granted_by_id=admin_users[0].id
                ))

        # Action Tickets
        for act_i in range(30):
            act_type = ActionTicketType.CREATE_CLUB if (act_i % 3 == 0) else (ActionTicketType.CREATE_EVENT_GENERAL if (act_i % 2 == 0) else ActionTicketType.EDIT_CLUB_ADMIN)
            creator_u = student_users[act_i % len(student_users)]
            t_status = TaskStatus.COMPLETED if (act_i % 2 == 0) else TaskStatus.OPEN
            
            a_ticket = ActionTicket(
                ticket_type=act_type,
                raised_by_id=creator_u.id,
                title=f"Action Ticket #{act_i + 1}: {act_type}",
                description=f"Action item raised by {creator_u.email} requiring administrative task execution.",
                reference_type="CLUB",
                reference_id=clubs_list[act_i % len(clubs_list)].id,
                reference_name=clubs_list[act_i % len(clubs_list)].club_name,
                task_status=t_status,
                assigned_to_id=admin_users[0].id
            )
            db.session.add(a_ticket)
            db.session.flush()

            log_action("ACTION_TICKET", a_ticket.id, admin_users[0].id, "Created Action Item", f"Ticket raised with status {t_status}")

        db.session.flush()

        print("12. Seeding User Notifications...")
        notification_types = ["GENERAL", "SYSTEM", "EVENT", "TICKET", "ANNOUNCEMENT"]
        notifications_count = 0

        # Seed rich, dynamic notifications based on real DB entities
        all_events = Event.query.all()
        all_clubs = Club.query.all()
        all_requests = Request.query.all()

        rich_notifications_templates = [
            {
                "type": "EVENT_CREATED",
                "entity_type": "EVENT",
                "title": "New Event: AI Hack Sprint",
                "message": "AI Club has created a new event scheduled for 20 Aug 2026.",
                "context": "AI Club · AI Hack Sprint",
                "ref": "/student/events/1"
            },
            {
                "type": "EVENT_SCHEDULE_CHANGED",
                "entity_type": "EVENT",
                "title": "Event Schedule Updated",
                "message": "The AI Hack Sprint has been rescheduled from 20 Aug to 22 Aug 2026.",
                "context": "AI Club · AI Hack Sprint",
                "ref": "/student/events/1"
            },
            {
                "type": "EVENT_REGISTERED",
                "entity_type": "EVENT",
                "title": "Registration Confirmed",
                "message": "You are registered for Stagecraft Workshop.",
                "context": "Drama Club · Stagecraft Workshop",
                "ref": "/student/events/2"
            },
            {
                "type": "TICKET",
                "entity_type": "TICKET",
                "title": "Ticket Assigned to You",
                "message": "You have been assigned to review ticket #104 for Robotics Club.",
                "context": "Robotics Club · Ticket #104",
                "ref": "/faculty/requests"
            },
            {
                "type": "TICKET",
                "entity_type": "TICKET",
                "title": "Ticket Approved",
                "message": "Your venue request for Robotics Club has been approved.",
                "context": "Robotics Club · Venue Request",
                "ref": "/student/requests"
            },
            {
                "type": "REQUEST",
                "entity_type": "REQUEST",
                "title": "Event Creation Request Approved",
                "message": "Your request to create Robotic Expo has been approved.",
                "context": "Robotics Club · Robotic Expo",
                "ref": "/student/requests"
            },
            {
                "type": "CLUB_CREATED",
                "entity_type": "CLUB",
                "title": "New Club Created",
                "message": "Robotics Club has been added to AllClub.",
                "context": "Robotics Club",
                "ref": "/student/clubs/1"
            },
            {
                "type": "VOLUNTEER_APPROVED",
                "entity_type": "VOLUNTEER",
                "title": "Volunteer Application Approved",
                "message": "You have been selected as Technical Support volunteer for Robotic Expo from 12 Sep to 14 Sep.",
                "context": "Robotics Club · Robotic Expo",
                "ref": "/student/roles"
            },
            {
                "type": "ROLE_ASSIGNED",
                "entity_type": "ROLE",
                "title": "Faculty Coordinator Role Assigned",
                "message": "You have been assigned as Faculty Coordinator for AI Club.",
                "context": "AI Club",
                "ref": "/faculty/roles"
            },
            {
                "type": "EVENT_ANNOUNCEMENT",
                "entity_type": "EVENT",
                "title": "New Event Announcement",
                "message": "AI Club has published an announcement for AI Hack Sprint: Venue shift to Seminar Hall A.",
                "context": "AI Club · AI Hack Sprint",
                "ref": "/student/events/1"
            },
            {
                "type": "EVENT_ATTENDANCE",
                "entity_type": "EVENT",
                "title": "Attendance Updated",
                "message": "Your attendance for Round 1 of AI Hack Sprint has been recorded as Present.",
                "context": "AI Club · AI Hack Sprint · Round 1",
                "ref": "/student/events/1"
            },
            {
                "type": "EVENT_WINNER",
                "entity_type": "EVENT",
                "title": "Event Results Announced",
                "message": "Results for AI Hack Sprint have been published.",
                "context": "AI Club · AI Hack Sprint",
                "ref": "/student/events/1"
            },
            {
                "type": "BUDGET_APPROVED",
                "entity_type": "BUDGET",
                "title": "Budget Request Approved",
                "message": "Your Robotics Club budget request for ₹25,000 has been approved.",
                "context": "Robotics Club · Budget Request",
                "ref": "/student/requests"
            }
        ]

        target_users = [admin_users[0], *faculty_users, *student_users[:40]]
        for idx, u in enumerate(target_users):
            user_notifs = rich_notifications_templates[idx % len(rich_notifications_templates): (idx % len(rich_notifications_templates)) + 5]
            for n_idx, notif in enumerate(user_notifs):
                ev = all_events[(idx + n_idx) % len(all_events)] if all_events else None
                cl = all_clubs[(idx + n_idx) % len(all_clubs)] if all_clubs else None
                rq = all_requests[(idx + n_idx) % len(all_requests)] if all_requests else None

                ent_id = ev.id if notif["entity_type"] == "EVENT" and ev else (cl.id if notif["entity_type"] == "CLUB" and cl else (rq.id if rq else 1))

                db.session.add(Notification(
                    user_id=u.id,
                    title=notif["title"],
                    message=notif["message"],
                    type=notif["type"],
                    entity_type=notif["entity_type"],
                    entity_id=ent_id,
                    context=notif["context"],
                    is_read=(n_idx % 2 == 0),
                    reference_url=notif["ref"],
                    created_at=datetime.utcnow() - timedelta(hours=n_idx * 5 + idx)
                ))
                notifications_count += 1

        db.session.commit()

        print("\n============================================================")
        print("ALLCLUB SEED COMPLETE — DATABASE SUMMARY:")
        print("============================================================")
        print(f"Users created:               {User.query.count()} (Admins: {len(admin_users)}, Faculty: {len(faculty_users)}, Students: {len(student_users)})")
        print(f"Clubs created:               {Club.query.count()}")
        print(f"Club Memberships:            {ClubMembership.query.count()}")
        print(f"Venues created:              {Venue.query.count()}")
        print(f"Events created:              {Event.query.count()}")
        print(f"Event Sessions / Rounds:     {EventSession.query.count()}")
        print(f"Participant Round Statuses:  {ParticipantRoundStatus.query.count()}")
        print(f"Event Registrations:         {EventRegistration.query.count()}")
        print(f"Event Attendance Records:    {EventAttendance.query.count()}")
        print(f"Event Announcements:         {EventAnnouncement.query.count()}")
        print(f"Event Prizes / Winners:      {EventPrize.query.count()}")
        print(f"Event Organizers & Vol:      {EventOrganizer.query.count()} Organizers / {EventVolunteer.query.count()} Volunteers")
        print(f"Requests & Approvals:        {Request.query.count()} Requests / {RequestApproval.query.count()} Approvals")
        print(f"Assignment & Action Tickets: {AssignmentTicket.query.count()} Assignment / {ActionTicket.query.count()} Action Tickets")
        print(f"Notifications:               {Notification.query.count()}")
        print("============================================================\n")

if __name__ == '__main__':
    app = create_app()
    seed_database(app)