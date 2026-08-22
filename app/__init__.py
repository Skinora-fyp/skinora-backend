from flask import Flask
from flask_cors import CORS
from .config import get_config
from .extensions import db, mail, bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Extensions
    CORS(app, resources={r'/api/*': {'origins': '*'}}, supports_credentials=True)
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    # Import all models so SQLAlchemy registers their tables
    with app.app_context():
        from .models import user, detection, question, questionnaire_response, remedy, tracking, checkin_notification, email_otp  # noqa
        db.create_all()

    # Blueprints
    from .routes.auth import auth_bp
    from .routes.detection import detection_bp
    from .routes.questionnaire import questionnaire_bp
    from .routes.remedies import remedies_bp
    from .routes.tracking import tracking_bp

    app.register_blueprint(auth_bp,          url_prefix='/api/auth')
    app.register_blueprint(detection_bp,     url_prefix='/api')
    app.register_blueprint(questionnaire_bp, url_prefix='/api/questionnaire')
    app.register_blueprint(remedies_bp,      url_prefix='/api/remedies')
    app.register_blueprint(tracking_bp,      url_prefix='/api/tracking')

    # Health check — use this to confirm backend + DB are working
    from flask import jsonify as _jsonify
    @app.route('/api/health')
    def health():
        try:
            db.session.execute(db.text('SELECT 1'))
            return _jsonify({'status': 'ok', 'db': 'connected'}), 200
        except Exception as e:
            return _jsonify({'status': 'error', 'db': str(e)}), 500

    # Background scheduler for reminder emails
    try:
        from .scheduler.reminder_jobs import start_scheduler
        start_scheduler(app)
    except Exception as e:
        app.logger.warning(f"Scheduler failed to start: {e}")

    return app
