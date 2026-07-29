from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    account_status = db.Column(db.String(20), nullable=False, default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = db.relationship('Role', lazy=True)
    student_profile = db.relationship('StudentProfile',backref='user',uselist=False,cascade="all, delete-orphan")
    faculty_profile = db.relationship('FacultyProfile',backref='user',uselist=False,cascade="all, delete-orphan")
    club_memberships = db.relationship("ClubMembership",back_populates="user",lazy=True,cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        created_str = (self.created_at.isoformat() if self.created_at else None)
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.email.split('@')[0],
            'fullName': self.email.split('@')[0],
            'phone': None,
            'registerNumber': None,
            'role': self.role.name if self.role else 'STUDENT',
            'roleId': self.role_id,
            'department': None,
            'departmentId': None,
            'year': None,
            'status': self.account_status,
            'bio': None,
            'createdAt': created_str
        }

        profile = self.student_profile or self.faculty_profile
        if profile:
            attr_map = {
                'name': 'full_name',
                'fullName': 'full_name',
                'phone': 'phone_number',
                'bio': 'bio',
                'year': 'year_of_study',
                'departmentId': 'department_id'
            }
            for key, attr in attr_map.items():
                if hasattr(profile, attr):
                    data[key] = getattr(profile, attr)

            data['registerNumber'] = (
                getattr(profile, 'roll_no', None)
                or getattr(profile, 'employee_id', None)
            )
            if profile.department:
                data['department'] = profile.department.name

        data['clubs'] = [membership.club.club_name for membership in self.club_memberships if membership.club]
        return data

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(30), nullable=True)
    year_of_study = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    department = db.relationship('Department', lazy=True)

    def to_dict(self):
        user_role = (
            self.user.role.name if (self.user and self.user.role) else 'STUDENT'
        )
        return {
            'id': self.id,
            'userId': self.user_id,
            'rollNo': self.roll_no,
            'registerNumber': self.roll_no,
            'fullName': self.full_name,
            'phone': self.phone_number,
            'yearOfStudy': self.year_of_study,
            'departmentId': self.department_id,
            'department': self.department.name if self.department else None,
            'role': user_role
        }

class FacultyProfile(db.Model):
    __tablename__ = 'faculty_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(30), nullable=True)
    designation = db.Column(db.String(100), nullable=True, default='Faculty Advisor')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    bio = db.Column(db.Text, nullable=True)

    department = db.relationship('Department', lazy=True)

    def to_dict(self):
        user_role = (
            self.user.role.name if (self.user and self.user.role) else 'FACULTY'
        )
        return {
            'id': self.id,
            'userId': self.user_id,
            'employeeId': self.employee_id,
            'registerNumber': self.employee_id,
            'fullName': self.full_name,
            'phone': self.phone_number,
            'designation': self.designation,
            'departmentId': self.department_id,
            'department': self.department.name if self.department else None,
            'role': user_role
        }

# ── Token Blocklist (For JWT Logout & Session Management) ──────────────
class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)