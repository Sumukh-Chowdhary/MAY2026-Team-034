from app import create_app
from app.models import (
    db, Role, Department, Permission, RolePermission,
    User, StudentProfile, FacultyProfile
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

        print("4. Seeding Core Users...")
        user_admin = User(
            email="admin@allclub.com",
            role_id=role_admin.id,
            account_status="ACTIVE"
        )
        user_admin.set_password("admin123")

        user_faculty = User(
            email="meena@allclub.com",
            role_id=role_faculty.id,
            account_status="ACTIVE"
        )
        user_faculty.set_password("faculty123")

        user_student = User(
            email="rahul@allclub.com",
            role_id=role_student.id,
            account_status="ACTIVE"
        )
        user_student.set_password("student123")

        db.session.add_all([user_admin, user_faculty, user_student])
        db.session.flush()

        print("5. Seeding Profiles...")
        prof_admin = StudentProfile(
            user_id=user_admin.id,
            roll_no="ADM001",
            full_name="Admin User",
            phone_number="+91 90000 00001",
            department_id=dept_admin.id,
            bio="Platform administrator managing all clubs, events, and users."
        )
        prof_faculty = FacultyProfile(
            user_id=user_faculty.id,
            employee_id="FAC001",
            full_name="Dr. Meena Rao",
            phone_number="+91 90000 00002",
            designation="Associate Professor",
            department_id=dept_cs.id,
            bio="Faculty advisor. Passionate about machine learning research."
        )
        prof_student = StudentProfile(
            user_id=user_student.id,
            roll_no="CB.SC.U4CSE22001",
            full_name="Rahul Sharma",
            phone_number="+91 98765 43210",
            year_of_study="3rd Year",
            department_id=dept_cs.id,
            bio="3rd year CSE student interested in Web Development and AI."
        )
        db.session.add_all([prof_admin, prof_faculty, prof_student])

        db.session.commit()
        print("Database successfully seeded for Module 1!")


if __name__ == '__main__':
    seed_database()
