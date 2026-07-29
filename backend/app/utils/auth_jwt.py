import uuid
from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import request, jsonify, current_app, g
from app.models import db, User, TokenBlocklist


def generate_jwt_token(user):
    """
    Generates a JWT access token containing user_id, role,
    and a unique jti identifier.
    """
    secret = current_app.config.get(
        'SECRET_KEY',
        'dev-secret-key-may2026-team034'
    )
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role.name if user.role else 'STUDENT',
        'jti': str(uuid.uuid4()),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=1)  # 24 hour token
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token, payload['jti']


def decode_jwt_token(token):
    """
    Decodes and validates a JWT token. Returns payload dict or raises Exception
    """
    secret = current_app.config.get(
        'SECRET_KEY',
        'dev-secret-key-may2026-team034')
    payload = jwt.decode(token, secret, algorithms=['HS256'])

    # Check if token is in blocklist
    jti = payload.get('jti')
    if jti and TokenBlocklist.query.filter_by(jti=jti).first():
        raise jwt.InvalidTokenError('Token has been revoked/logged out')

    return payload


def jwt_required(f):
    """
    Decorator requiring a valid JWT bearer token in Authorization header.
    Attaches current user object to flask 'g.current_user' and 'g.jti'.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'error': 'Authorization header format must be Bearer <token>'
                }), 401

        token = parts[1]
        try:
            payload = decode_jwt_token(token)
            user = db.session.get(User, payload['user_id'])
            if not user or user.account_status != 'ACTIVE':
                return jsonify({
                    'error': 'User account is inactive or disabled'
                    }), 403

            g.current_user = user
            g.jti = payload.get('jti')
            g.jwt_payload = payload
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': str(e)}), 401
        except Exception:
            return jsonify({'error': 'Invalid authentication token'}), 401

        return f(*args, **kwargs)
    return decorated


def roles_required(*roles):
    """
    Decorator enforcing role-based authorization
    (e.g. @roles_required('ADMIN', 'FACULTY')).
    Must be placed AFTER @jwt_required.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user or not user.role:
                return jsonify({
                    'error': 'Access denied. Authorization role missing'
                    }), 403

            user_role = user.role.name.upper()
            allowed_roles = [r.upper() for r in roles]
            if user_role not in allowed_roles:
                msg = (
                    "Access denied. Requires one of roles: "
                    f"{allowed_roles}"
                )
                return jsonify({'error': msg}), 403

            return f(*args, **kwargs)
        return decorated
    return decorator
