from flask import Blueprint, request, jsonify, g
from app.models import (
    db, User, Role, Department, StudentProfile, FacultyProfile, TokenBlocklist
)
from app.utils.auth_jwt import generate_jwt_token, jwt_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = str(data.get('username') or data.get('registerNumber') or data.get('email') or '').strip()
    password = data.get('password')

    if not username or not password:
        return jsonify(
            {'error': 'Registration ID/Email and Password are required'}
        ), 400

    # Find user by email, registration ID / roll number, or employee ID
    user = None
    if '@' in username:
        user = User.query.filter_by(email=username).first()
        if user and user.role and user.role.name == 'STUDENT':
            return jsonify({'error': 'Students must log in using their Registration ID'}), 400
    
    if not user:
        student_prof = StudentProfile.query.filter(
            (StudentProfile.roll_no == username) | 
            (StudentProfile.registration_id == username)
        ).first()
        if student_prof:
            user = student_prof.user
        else:
            faculty_prof = FacultyProfile.query.filter_by(employee_id=username).first()
            if faculty_prof:
                user = faculty_prof.user

    if not user or not user.check_password(password):
        return jsonify(
            {'error': 'Invalid Registration ID/Email or password'}
        ), 401

    if user.account_status == 'INACTIVE':
        return jsonify(
            {'error': 'Your account has been deactivated. Please contact admin.'}
        ), 403

    token, jti = generate_jwt_token(user)

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    full_name = data.get('fullName')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone')
    role_name = (data.get('role') or 'STUDENT').upper()
    department_id = data.get('departmentId')
    register_number = data.get('registerNumber')
    year_of_study = data.get('year')

    if not full_name or not email or not password:
        return jsonify(
            {'error': 'Full Name, Email, and Password are required'}
        ), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'A user with this email already exists'}), 400

    # Find or create Role
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name, description=f'{role_name} role')
        db.session.add(role)
        db.session.flush()

    # Match Department
    department = None
    if department_id:
        department = Department.query.get(department_id)

    dept_id = department.id if department else None

    # Create User record
    user = User(
        email=email,
        role_id=role.id,
        account_status='ACTIVE'
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # Attach Student or Faculty profile
    if role_name == 'FACULTY':
        emp_id = register_number or f"FAC{user.id:04d}"
        if FacultyProfile.query.filter_by(employee_id=emp_id).first():
            db.session.rollback()
            return jsonify({'error': 'Employee ID already exists'}), 400
        prof = FacultyProfile(
            user_id=user.id,
            employee_id=emp_id,
            full_name=full_name,
            phone_number=phone_number,
            department_id=dept_id
        )
        db.session.add(prof)
    elif role_name == 'STUDENT':
        from app.utils.registration_id import generate_registration_id, get_branch_code, parse_registration_id

        dept_code = department.code if department else 'CS'
        batch_yr = 2026
        if register_number and str(register_number).strip() and not str(register_number).startswith('STU'):
            roll_no = str(register_number).strip().upper()
        else:
            roll_no = generate_registration_id(batch_yr, dept_code, user.id)

        if StudentProfile.query.filter_by(roll_no=roll_no).first():
            db.session.rollback()
            return jsonify({'error': 'Register/Roll number already exists'}), 400

        parsed = parse_registration_id(roll_no)
        b_yr = (int(parsed["batchYear"]) + 2000) if parsed else batch_yr
        br_code = parsed["branchCode"] if parsed else get_branch_code(dept_code)
        r_num = int(parsed["rollNumber"]) if parsed else user.id

        prof = StudentProfile(
            user_id=user.id,
            roll_no=roll_no,
            registration_id=roll_no,
            batch_year=b_yr,
            branch_code=br_code,
            roll_number=r_num,
            graduation_year=b_yr + 4,
            full_name=full_name,
            phone_number=phone_number,
            year_of_study=year_of_study,
            department_id=dept_id
        )
        db.session.add(prof)

    db.session.commit()
    token, jti = generate_jwt_token(user)

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/logout', methods=['POST'])
@jwt_required
def logout():
    jti = getattr(g, 'jti', None)
    if jti:
        blocked = TokenBlocklist(jti=jti)
        db.session.add(blocked)
        db.session.commit()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required
def change_password():
    data = request.get_json() or {}
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if not old_password or not new_password:
        return jsonify(
            {'error': 'Old password and new password are required'}
        ), 400

    user = g.current_user
    if not user.check_password(old_password):
        return jsonify({'error': 'Current password is incorrect'}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_me():
    user = g.current_user
    return jsonify(user.to_dict()), 200
