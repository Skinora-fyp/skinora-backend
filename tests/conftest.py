"""
Skinora Backend — Pytest Configuration
Fixtures shared across all test modules.

Uses an SQLite in-memory-style file DB so no MySQL is required.
The real app DB is never touched during test runs.
"""
import os
import pathlib
import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch

# ── Must be set BEFORE create_app is imported ──────────────────────────────
# load_dotenv() inside config.py does NOT override env vars already set here.
TEST_DB_PATH = pathlib.Path(__file__).parent / 'test_skinora.db'
os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB_PATH}'
os.environ.setdefault('SECRET_KEY', 'test-secret-key-skinora')

# Now safe to import the app
from app import create_app
from app.extensions import db as _db, bcrypt as _bcrypt
from app.models.user import User
from app.models.remedy import Remedy, ConditionRemedy
from app.models.tracking import Tracking
from app.models.email_otp import EmailOTP


# ── App fixture ─────────────────────────────────────────────────────────────
@pytest.fixture(scope='session')
def app():
    """
    Create a Flask application configured for testing.
    - Uses SQLite (no MySQL required).
    - Scheduler is patched out so no background threads start.
    - Mail sending is suppressed.
    """
    # Patch the scheduler so it never starts during tests
    with patch('app.scheduler.reminder_jobs.start_scheduler'):
        flask_app = create_app()

    flask_app.config.update({
        'TESTING': True,
        'MAIL_SUPPRESS_SEND': True,
        # Allow SQLite to be used from multiple threads safely
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'connect_args': {'check_same_thread': False}
        },
    })

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()
        _db.engine.dispose()  # release all connections before unlinking the file

    # Remove the SQLite file — ignore if Windows still holds a lock
    try:
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
    except PermissionError:
        pass  # file will be cleaned up on next run or OS restart


@pytest.fixture(scope='session')
def client(app):
    """Flask test client used by all tests."""
    return app.test_client()


# ── Shared database fixtures ────────────────────────────────────────────────
@pytest.fixture(scope='session')
def test_user(app):
    """
    A pre-created, verified user for login and protected-route tests.
    Returns the user ID (not the ORM object) to avoid detached-instance issues
    across session scope.
    """
    with app.app_context():
        existing = User.query.filter_by(email='skinora_test@gmail.com').first()
        if existing:
            return existing.id
        pw_hash = _bcrypt.generate_password_hash('TestPass123!', rounds=4).decode('utf-8')
        user = User(
            name='Skinora Tester',
            email='skinora_test@gmail.com',
            password_hash=pw_hash,
            is_verified=True,
        )
        _db.session.add(user)
        _db.session.commit()
        return user.id


@pytest.fixture(scope='session')
def auth_headers(app, test_user):
    """
    Authorization headers (Bearer JWT) for the test user.
    Attach these to any request that hits a @token_required endpoint.
    """
    payload = {
        'user_id': test_user,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }


@pytest.fixture(scope='session')
def test_remedy(app):
    """
    A pre-seeded Remedy + ConditionRemedy mapping used in tracking tests.
    Returns the remedy ID.
    """
    with app.app_context():
        existing = Remedy.query.filter_by(name='Test Aloe Vera Mask').first()
        if existing:
            return existing.id
        remedy = Remedy(
            name='Test Aloe Vera Mask',
            ingredients=['aloe vera gel', 'rosewater'],
            instructions=['Mix ingredients', 'Apply to face', 'Rinse after 15 min'],
            confidence_level='High',
            lifestyle_tags=['low_water'],
        )
        _db.session.add(remedy)
        _db.session.commit()
        _db.session.add(ConditionRemedy(
            final_condition='Oily_Acne',
            remedy_id=remedy.id,
            sort_order=1,
        ))
        _db.session.commit()
        return remedy.id


@pytest.fixture(scope='session')
def test_tracking(app, test_user, test_remedy):
    """
    A pre-created Tracking record tied to test_user and test_remedy.
    Returns the tracking ID. Used for toggle-reminders and checkin tests.
    """
    with app.app_context():
        existing = Tracking.query.filter_by(user_id=test_user, remedy_id=test_remedy).first()
        if existing:
            return existing.id
        tracking = Tracking(
            user_id=test_user,
            remedy_id=test_remedy,
            frequency='weekly',
            next_reminder=datetime.utcnow() + timedelta(days=7),
            is_active=True,
        )
        _db.session.add(tracking)
        _db.session.commit()
        return tracking.id
