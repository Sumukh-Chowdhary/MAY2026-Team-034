import os
from flask import Flask
from flask_cors import CORS
from config import Config, INSTANCE_DIR
from app.models import db
from app.extensions import socketio

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))


def create_app(config_class=Config):
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    frontend_dist = os.path.abspath(
        os.path.join(ROOT_DIR, 'frontend', 'dist')
    )

    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder=frontend_dist,
        static_url_path='',
        template_folder=frontend_dist,
    )
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.admin import admin_bp
    from app.routes.events import events_bp
    from app.routes.venues import venues_bp
    from app.routes.student import student_bp
    from app.routes.requests import requests_bp
    from app.routes.action_tickets import action_tickets_bp
    from app.routes.assignment_tickets import assignments_bp
    from app.routes.request_views import request_views_bp
    from app.routes.faculty import faculty_bp
    from app.routes.clubpage import club_bp
    from app.routes.notifications import notifications_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(venues_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(action_tickets_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(request_views_bp)
    app.register_blueprint(club_bp)
    app.register_blueprint(notifications_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'Flask API is running'}, 200

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path.startswith('api/'):
            return {'message': 'Not Found'}, 404

        if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
            return app.send_static_file(path)

        return app.send_static_file('index.html')

    with app.app_context():
        db.create_all()

    return app
