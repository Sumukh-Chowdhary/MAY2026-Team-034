from datetime import datetime

from app import create_app
from app.models.user import (
    db,
    Role,
    Department,
    User,
    StudentProfile,
    FacultyProfile,
)
from app.models.club import (
    Club,
    ClubFaculty,
    ClubMembership,
    ClubOrganizer,
)

from app.models.event_details import (
    EventSchedule,
    Announcement,
    EventRegistration,
    Attendance,
)

from app.models.events import Event, Venue

from .seed_data import (
    ADMIN_DATA,
    FACULTY_DATA,
    STUDENT_DATA,
    CLUB_DATA,
    VENUE_DATA,
    EVENT_DATA,
    SCHEDULE_DATA,
    ANNOUNCEMENT_DATA,
    REGISTRATION_DATA,
    ATTENDANCE_DATA
)


def seed_database(app):
    with app.app_context():
        print("Re-creating all tables...")
        db.drop_all()
        db.create_all()

        # ==========================================================
        # 1. Roles
        # ==========================================================
        print("1. Seeding Roles...")

        role_admin = Role(
            name="ADMIN",
            description="Platform Administrator",
        )

        role_faculty = Role(
            name="FACULTY",
            description="Faculty Advisor & Reviewer",
        )

        role_student = Role(
            name="STUDENT",
            description="Student Member / Lead",
        )

        db.session.add_all([
            role_admin,
            role_faculty,
            role_student,
        ])
        db.session.flush()

        # ==========================================================
        # 2. Departments
        # ==========================================================
        print("2. Seeding Departments...")

        dept_admin = Department(
            name="Administration",
            code="ADM",
        )

        dept_cs = Department(
            name="Computer Science",
            code="CSE",
        )

        dept_ece = Department(
            name="Electronics",
            code="ECE",
        )

        db.session.add_all([
            dept_admin,
            dept_cs,
            dept_ece,
        ])
        db.session.flush()

        department_map = {
            dept.code: dept.id
            for dept in [dept_admin, dept_cs, dept_ece]
        }

        # ==========================================================
        # 3. Users
        # ==========================================================
        print("3. Seeding Users...")

        user_admin = User(
            email=ADMIN_DATA["email"],
            role_id=role_admin.id,
            account_status="ACTIVE",
        )
        user_admin.set_password(ADMIN_DATA["password"])

        faculty_users = []

        for faculty in FACULTY_DATA:
            user = User(
                email=faculty["email"],
                role_id=role_faculty.id,
                account_status="ACTIVE",
            )
            user.set_password(faculty["password"])
            faculty_users.append(user)

        student_users = []

        for student in STUDENT_DATA:
            user = User(
                email=student["email"],
                role_id=role_student.id,
                account_status="ACTIVE",
            )
            user.set_password(student["password"])
            student_users.append(user)

        db.session.add_all([
            user_admin,
            *faculty_users,
            *student_users,
        ])
        db.session.flush()

        # ==========================================================
        # 4. Profiles
        # ==========================================================
        print("4. Seeding Profiles...")

        admin_profile = StudentProfile(
            user_id=user_admin.id,
            roll_no=ADMIN_DATA["roll_no"],
            full_name=ADMIN_DATA["full_name"],
            phone_number=ADMIN_DATA["phone_number"],
            year_of_study=ADMIN_DATA["year_of_study"],
            department_id=department_map[ADMIN_DATA["department"]],
            bio=ADMIN_DATA["bio"],
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
                bio=faculty["bio"],
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
                bio=student["bio"],
            )
            db.session.add(profile)

        db.session.flush()

        # ==========================================================
        # 5. Clubs
        # ==========================================================
        print("5. Seeding Clubs...")

        faculty_lookup = {
            faculty["employee_id"]: user
            for faculty, user in zip(FACULTY_DATA, faculty_users)
        }

        student_lookup = {
            student["roll_no"]: user
            for student, user in zip(STUDENT_DATA, student_users)
        }

        for club in CLUB_DATA:
            new_club = Club(
                club_name=club["name"],
                club_description=club["description"],
                club_category=club["category"],
                club_logo=club["logo"],
                club_status="ACTIVE",
                total_members=1,
                active_members=1,
            )

            db.session.add(new_club)
            db.session.flush()

            db.session.add(
                ClubFaculty(
                    club_id=new_club.id,
                    faculty_id=faculty_lookup[club["faculty"]].id,
                    faculty_role="FACULTY_COORDINATOR",
                )
            )

            organizer = student_lookup[club["organizer"]]

            db.session.add(
                ClubOrganizer(
                    club_id=new_club.id,
                    user_id=organizer.id,
                    organizer_role="PRESIDENT",
                )
            )

            db.session.add(
                ClubMembership(
                    club_id=new_club.id,
                    user_id=organizer.id,
                    membership_role="MEMBER",
                    membership_status="ACTIVE",
                )
            )

        # ==========================================================
        # 6. Venues
        # ==========================================================
        print("6. Seeding Venues...")

        venue_lookup = {}

        for venue in VENUE_DATA:
            new_venue = Venue(
                venue_name=venue["name"],
                venue_location=venue["location"],
                venue_type=venue["type"],
                capacity=venue["capacity"],
            )

            db.session.add(new_venue)
            db.session.flush()

            venue_lookup[venue["name"]] = new_venue

        # ==========================================================
        # 7. Events
        # ==========================================================
        print("7. Seeding Events...")

        club_lookup = {
            club.club_name: club
            for club in Club.query.all()
        }

        for event in EVENT_DATA:
            creator = faculty_lookup[event["created_by"]]

            new_event = Event(
                club_id=club_lookup[event["club"]].id,
                venue_id=venue_lookup[event["venue"]].id,
                created_by=creator.id,
                event_name=event["name"],
                event_description=event["description"],
                event_status=event["status"],
                start_date=datetime.strptime(
                    event["start_date"],
                    "%Y-%m-%d",
                ).date(),
                end_date=datetime.strptime(
                    event["end_date"],
                    "%Y-%m-%d",
                ).date(),
                capacity=event["capacity"],
            )

            db.session.add(new_event)

        # Flush so Events receive IDs before querying them
        db.session.flush()

        event_lookup = {
            event.event_name: event
            for event in Event.query.all()
        }

        # ==========================================================
        # 8. Event Schedule
        # ==========================================================
        print("8. Seeding Event Schedule...")

        for item in SCHEDULE_DATA:
            db.session.add(
                EventSchedule(
                    event_id=event_lookup[item["event"]].id,
                    time=item["time"],
                    activity=item["activity"],
                )
            )

        # ==========================================================
        # 9. Announcements
        # ==========================================================
        print("9. Seeding Announcements...")

        for item in ANNOUNCEMENT_DATA:
            db.session.add(
                Announcement(
                    event_id=event_lookup[item["event"]].id,
                    title=item["title"],
                    message=item["message"],
                )
            )

        # ==========================================================
        # 10. Registrations
        # ==========================================================
        print("10. Seeding Registrations...")

        for item in REGISTRATION_DATA:
            db.session.add(
                EventRegistration(
                    event_id=event_lookup[item["event"]].id,
                    student_id=student_lookup[item["student"]].id,
                )
            )

        # ==========================================================
        # 11. Attendance
        # ==========================================================
        print("11. Seeding Attendance...")

        for item in ATTENDANCE_DATA:
            db.session.add(
                Attendance(
                    event_id=event_lookup[item["event"]].id,
                    student_id=student_lookup[item["student"]].id,
                    status=item["status"],
                )
            )

        # ==========================================================
        # Commit
        # ==========================================================
        db.session.commit()

        print("Database successfully seeded!")

if __name__ == "__main__":
    app = create_app()
    seed_database(app)