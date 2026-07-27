from app import create_app
from app.models import (
    db, Role, Department, Permission, RolePermission,
    User, StudentProfile, FacultyProfile, Club
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
            "ADM": dept_admin.id,
            "CSE": dept_cs.id,
            "ECE": dept_ece.id,
        }

        print("3. Seeding Permissions...")
        p_manage = Permission(
            name="MANAGE_USERS", description="Manage user accounts"
        )
        p_clubs = Permission(
            name="APPROVE_CLUBS", description="Review club requests"
        )
        p_events = Permission(
            name="APPROVE_EVENTS", description="Review event requests"
        )
        db.session.add_all([p_manage, p_clubs, p_events])
        db.session.flush()

        db.session.add_all([
            RolePermission(
                role_id=role_admin.id, permission_id=p_manage.id
            ),
            RolePermission(
                role_id=role_admin.id, permission_id=p_clubs.id
            ),
            RolePermission(
                role_id=role_faculty.id, permission_id=p_events.id
            )
        ])

        ADMIN_DATA = {
            "email": "admin@allclub.com",
            "password": "admin123",
            "roll_no": "ADM001",
            "full_name": "Admin User",
            "phone_number": "+91 90000 00001",
            "year_of_study": None,
            "department_id": department_map["ADM"],
            "bio": "Platform administrator managing all clubs, events, and users."
        }

        FACULTY_DATA = [
            {
                "email": "meena@allclub.com",
                "password": "faculty123",
                "employee_id": "FAC001",
                "full_name": "Dr. Meena Rao",
                "phone_number": "+91 90000 00002",
                "department_id": department_map["CSE"],
                "designation": "Associate Professor",
                "bio": "Faculty advisor. Passionate about machine learning research."
            }
        ]

        STUDENT_DATA = [
            {
                "email": "rahul@allclub.com",
                "password": "student123",
                "roll_no": "STU001",
                "full_name": "Rahul Sharma",
                "phone_number": "+91 90000 00003",
                "year_of_study": "3rd Year",
                "department_id": department_map["CSE"],
                "bio": "Computer science student interested in web development."
            }
        ]

        print("4. Seeding Users...")
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

        print("5. Seeding Profiles...")
        admin_profile = StudentProfile(
            user_id=user_admin.id,
            roll_no=ADMIN_DATA["roll_no"],
            full_name=ADMIN_DATA["full_name"],
            phone_number=ADMIN_DATA["phone_number"],
            year_of_study=ADMIN_DATA["year_of_study"],
            department_id=ADMIN_DATA["department_id"],
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
                department_id=faculty["department_id"],
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
                department_id=student["department_id"],
                bio=student["bio"]
            )
            db.session.add(profile)

        db.session.flush()

        # print("6. Seeding Clubs...")

        # club_ai = Club(...)
        # club_music = Club(...)
        # ...
        # db.session.add_all([
        #     club_ai,
        #     club_music,
        #     ...
        # ])
        # db.session.flush()

        db.session.commit()
        print("Database successfully seeded!")


if __name__ == '__main__':
    seed_database()
