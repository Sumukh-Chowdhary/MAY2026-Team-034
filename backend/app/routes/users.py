from flask import Blueprint, request, jsonify, g
from app.models import db, User, Role
from app.utils.auth_jwt import jwt_required, roles_required

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['GET'])
@jwt_required
def get_users():
    role_name = request.args.get('role')
    search_q = request.args.get('search')

    current_user = g.current_user
    viewer_role = current_user.role.name if (current_user and current_user.role) else 'STUDENT'

    query = User.query

    if role_name:
        role = Role.query.filter_by(name=role_name.upper()).first()
        if role:
            query = query.filter(User.role_id == role.id)

    users = query.all()
    results = []
    for u in users:
        u_dict = u.to_dict()
        is_self = (current_user and current_user.id == u.id)
        if viewer_role == 'STUDENT' and not is_self:
            u_dict['phone'] = None
            u_dict['phoneNumber'] = None
        results.append(u_dict)

    if search_q:
        q = search_q.lower()
        results = [
            u for u in results
            if (
                q in u['name'].lower()
                or q in u['email'].lower()
                or (u['registerNumber'] and q in u['registerNumber'].lower())
            )
        ]

    return jsonify(results), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)

    current_user = g.current_user
    viewer_role = current_user.role.name if (current_user and current_user.role) else 'STUDENT'
    is_self = (current_user and current_user.id == user.id)

    data = user.to_dict()
    if viewer_role == 'STUDENT' and not is_self:
        data['phone'] = None
        data['phoneNumber'] = None

    return jsonify(data), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    current_user = g.current_user

    # Allow update if updating self or if current user is Admin
    is_admin = current_user.role and current_user.role.name == 'ADMIN'
    if current_user.id != user.id and not is_admin:
        return jsonify(
            {'error': 'You do not have permission to update this profile'}
        ), 403

    data = request.get_json() or {}
    profile = user.student_profile or user.faculty_profile

    if profile:
        field_mapping = {
            'fullName': 'full_name',
            'name': 'full_name',
            'phone': 'phone_number',
            'phoneNumber': 'phone_number',
            'departmentId': 'department_id',
            'year': 'year_of_study',
            'yearOfStudy': 'year_of_study',
            'designation': 'designation',
            'bio': 'bio',
            'avatarStyle': 'avatar_style',
            'avatarSeed': 'avatar_seed'
        }
        for key, attr in field_mapping.items():
            if key in data and hasattr(profile, attr):
                setattr(profile, attr, data[key])

    # Status update (Admin only)
    new_status = data.get('accountStatus') or data.get('status')
    if new_status and is_admin:
        user.account_status = new_status
        if new_status == 'LEGACY':
            for membership in user.club_memberships:
                if not membership.ended_at:
                    membership.ended_at = datetime.utcnow()
        elif new_status == 'ACTIVE':
            for membership in user.club_memberships:
                membership.ended_at = None

    db.session.commit()
    return jsonify(user.to_dict()), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required
@roles_required('ADMIN')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {user_id} deleted successfully'}), 200
