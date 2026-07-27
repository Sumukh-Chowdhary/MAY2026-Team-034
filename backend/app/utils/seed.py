from app import create_app
from app.models.user import (
    db, Role, Department,User, StudentProfile, FacultyProfile
)

from app.models.club import (
    Club,ClubFaculty,ClubMembership,ClubOrganizer
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
        role_admin = Role(
            name="ADMIN", description="Platform Administrator"
        )
        role_faculty = Role(
            name="FACULTY", description="Faculty Advisor & Reviewer"
        )
        role_student = Role(
            name="STUDENT", description="Student Member / Lead"
        )
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

        for faculty in FACULTY_DATA:
            user = User(
                email=faculty["email"],
                role_id=role_faculty.id,
                account_status="ACTIVE"
            )

            user.set_password(faculty["password"])
            faculty_users.append(user)

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

        for club in CLUB_DATA:

            # Create Club
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

            # Assign Faculty Coordinator
            db.session.add(
                ClubFaculty(
                    club_id=new_club.id,
                    faculty_id=faculty_lookup[club["faculty"]].id,
                    faculty_role="FACULTY_COORDINATOR"
                )
            )

            # Assign Student Organizer
            organizer = student_lookup[club["organizer"]]

            db.session.add(
                ClubOrganizer(
                    club_id=new_club.id,
                    user_id=organizer.id,
                    organizer_role="PRESIDENT"
                )
            )

            # Organizer is also a club member
            db.session.add(
                ClubMembership(
                    club_id=new_club.id,
                    user_id=organizer.id,
                    membership_role="MEMBER",
                    membership_status="ACTIVE"
                )
            )

        db.session.commit()

        print("Database successfully seeded!")

if __name__ == '__main__':
    seed_database()