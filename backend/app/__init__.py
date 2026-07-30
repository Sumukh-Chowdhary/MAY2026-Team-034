import os
from flask import Flask
from flask_cors import CORS
from config import Config, INSTANCE_DIR
from app.models import db


def create_app(config_class=Config):
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.admin import admin_bp
    from app.routes.events import events_bp
    from app.routes.venues import venues_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(venues_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'Flask API is running'}, 200

    with app.app_context():
        db.create_all()

    return app
