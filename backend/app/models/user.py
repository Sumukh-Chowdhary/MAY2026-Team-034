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
    club_memberships = db.relationship('ClubMembership', back_populates='user', lazy=True, cascade="all, delete-orphan")

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

            if hasattr(profile, 'roll_no'):
                reg_id = getattr(profile, 'registration_id', None) or profile.roll_no
                data['registerNumber'] = reg_id
                data['rollNo'] = reg_id
                data['registrationId'] = reg_id
                data['batchYear'] = getattr(profile, 'batch_year', None)
                data['branchCode'] = getattr(profile, 'branch_code', None)
                data['rollNumber'] = getattr(profile, 'roll_number', None)
                data['graduationYear'] = getattr(profile, 'graduation_year', None)
            elif hasattr(profile, 'employee_id'):
                data['registerNumber'] = profile.employee_id
                data['employeeId'] = profile.employee_id

            if profile.department:
                data['department'] = profile.department.name

            data['avatarStyle'] = getattr(profile, 'avatar_style', None) or 'adventurer'
            data['avatarSeed'] = getattr(profile, 'avatar_seed', None) or data['fullName']

        if 'avatarStyle' not in data or not data['avatarStyle']:
            data['avatarStyle'] = 'adventurer'
        if 'avatarSeed' not in data or not data['avatarSeed']:
            data['avatarSeed'] = data.get('fullName') or data.get('name') or data.get('email', 'User')

        data['isLegacy'] = (self.account_status == 'LEGACY')
        data['clubs'] = [membership.club.club_name for membership in self.club_memberships if membership.club]
        return data

    @property
    def is_legacy(self):
        return self.account_status == 'LEGACY'

    def check_and_update_lifecycle(self):
        """Auto-update student lifecycle status to LEGACY if graduation_year <= current year."""
        if self.role and self.role.name == 'STUDENT' and self.student_profile:
            current_year = datetime.utcnow().year
            grad_year = self.student_profile.graduation_year
            if grad_year and grad_year <= current_year and self.account_status == 'ACTIVE':
                self.account_status = 'LEGACY'
                for membership in self.club_memberships:
                    if not membership.ended_at:
                        membership.ended_at = datetime.utcnow()
                db.session.commit()

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False) # Stores formatted Registration ID (e.g. Y26CS001)
    registration_id = db.Column(db.String(50), unique=True, nullable=True)
    batch_year = db.Column(db.Integer, nullable=True)
    branch_code = db.Column(db.String(10), nullable=True)
    roll_number = db.Column(db.Integer, nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(30), nullable=True)
    year_of_study = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_style = db.Column(db.String(50), default='adventurer')
    avatar_seed = db.Column(db.String(100), nullable=True)

    department = db.relationship('Department', lazy=True)

    def to_dict(self):
        user_role = (
            self.user.role.name if (self.user and self.user.role) else 'STUDENT'
        )
        user_status = self.user.account_status if self.user else 'ACTIVE'
        reg_id = self.registration_id or self.roll_no
        return {
            'id': self.id,
            'userId': self.user_id,
            'rollNo': reg_id,
            'registerNumber': reg_id,
            'registrationId': reg_id,
            'batchYear': self.batch_year,
            'branchCode': self.branch_code,
            'rollNumber': self.roll_number,
            'graduationYear': self.graduation_year,
            'fullName': self.full_name,
            'phone': self.phone_number,
            'yearOfStudy': self.year_of_study,
            'departmentId': self.department_id,
            'department': self.department.name if self.department else None,
            'role': user_role,
            'status': user_status,
            'isLegacy': (user_status == 'LEGACY'),
            'avatarStyle': self.avatar_style or 'adventurer',
            'avatarSeed': self.avatar_seed or self.full_name
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
    avatar_style = db.Column(db.String(50), default='adventurer')
    avatar_seed = db.Column(db.String(100), nullable=True)

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
            'role': user_role,
            'avatarStyle': self.avatar_style or 'adventurer',
            'avatarSeed': self.avatar_seed or self.full_name
        }

# ── Token Blocklist (For JWT Logout & Session Management) ──────────────
class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
