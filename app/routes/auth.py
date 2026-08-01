import jwt
import requests as http
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from ..extensions import db, bcrypt
from ..models.user import User
from ..services.email_service import send_welcome_email

auth_bp = Blueprint('auth', __name__)


def _generate_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    password_hash = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        is_verified=True,
    )
    db.session.add(user)
    db.session.commit()

    email_sent = send_welcome_email(user)

    return jsonify({
        'message': 'Registration Successful',
        'email_sent': email_sent,
    }), 201


@auth_bp.route('/verify', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Verification token required'}), 400

    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({'error': 'Invalid or expired verification token'}), 400

    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    access_token = _generate_token(user.id)
    return jsonify({
        'message': 'Email verified successfully',
        'access_token': access_token,
        'user': user.to_dict(),
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash:
        return jsonify({'error': 'Invalid email or password'}), 401
    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = _generate_token(user.id)
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict(),
    }), 200


@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    """
    Accepts { access_token } from the frontend (obtained via Google OAuth implicit flow).
    Verifies with Google's userinfo endpoint, then creates or finds the local user.
    """
    import traceback
    try:
        data = request.get_json() or {}
        access_token = data.get('access_token')

        if not access_token:
            return jsonify({'error': 'Google access_token required'}), 400

        # Verify with Google userinfo endpoint
        resp = http.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        if resp.status_code != 200:
            return jsonify({'error': 'Could not verify Google token'}), 401

        info = resp.json()
        google_id = info.get('sub')
        email = (info.get('email') or '').lower()
        name = info.get('name') or email.split('@')[0]
        avatar_url = info.get('picture')

        if not google_id or not email:
            return jsonify({'error': 'Incomplete Google profile data'}), 400

        # Find or create user
        is_new_user = False
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                # Existing email account — link Google ID
                if not user.google_id:
                    user.google_id = google_id
                if avatar_url and not user.avatar_url:
                    user.avatar_url = avatar_url
                user.is_verified = True
            else:
                user = User(
                    name=name, email=email,
                    google_id=google_id, avatar_url=avatar_url,
                    is_verified=True,
                )
                db.session.add(user)
                is_new_user = True

        db.session.commit()

        if is_new_user:
            send_welcome_email(user)

        access_token_jwt = _generate_token(user.id)

        return jsonify({
            'access_token': access_token_jwt,
            'user': user.to_dict(),
        }), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"google_login error: {traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
