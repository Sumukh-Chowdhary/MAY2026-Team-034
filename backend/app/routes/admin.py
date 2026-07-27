from flask import Blueprint, request, jsonify
from app.models import db, User, Role, Department
from app.utils.auth_jwt import jwt_required, roles_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@jwt_required
@roles_required('ADMIN')
@admin_bp.get('/clubs')
def get_clubs():
    return