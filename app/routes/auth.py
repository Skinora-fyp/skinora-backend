import jwt
import re
import random
import socket
import requests as http
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from ..extensions import db, bcrypt
from ..models.user import User
from ..models.email_otp import EmailOTP
from ..services.email_service import send_welcome_email, send_otp_email

auth_bp = Blueprint('auth', __name__)

# ── Email validation helpers ──────────────────────────────────

_EMAIL_RE = re.compile(
    r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
)

_DISPOSABLE_DOMAINS = {
    'mailinator.com', 'guerrillamail.com', 'guerrillamail.info',
    'guerrillamail.biz', 'guerrillamail.de', 'guerrillamail.net',
    'guerrillamail.org', 'grr.la', 'sharklasers.com',
    'yopmail.com', 'yopmail.fr', 'cool.fr.nf', 'jetable.fr.nf',
    'nospam.ze.tc', 'nomail.xl.cx', 'mega.zik.dj', 'speed.1s.fr',
    'courriel.fr.nf', 'moncourrier.fr.nf', 'monemail.fr.nf',
    'monmail.fr.nf', 'maildrop.cc', 'spam4.me', 'trashmail.com',
    'trashmail.me', 'trashmail.net', 'trashmail.at', 'trashmail.io',
    'tempmail.com', 'temp-mail.org', 'tempr.email', 'dispostable.com',
    'mailnull.com', 'spamgourmet.com', 'spamgourmet.net',
    'spamgourmet.org', 'mailexpire.com', 'jetable.org',
    'spambox.us', 'getonemail.com', 'filzmail.com',
    'discard.email', 'fakeinbox.com', 'tempinbox.com',
    'throwaway.email', 'throwam.com', 'mailtemp.info',
    'mytemp.email', 'emailondeck.com', 'tempm.com',
    'getnada.com', 'mailnesia.com', 'mailnull.com',
    'spamgourmet.com', 'anonbox.net', 'spamhereplease.com',
    'spamthisplease.com', 'binkmail.com', 'bobmail.info',
    'tempail.com', 'spamfree24.org', 'incognitomail.com',
}


def _is_valid_email_format(email: str) -> bool:
    return bool(_EMAIL_RE.match(email))


def _domain_has_dns(domain: str) -> bool:
    """Return True if the domain resolves in DNS (A, AAAA, or MX via CNAME)."""
    try:
        socket.getaddrinfo(domain, None, proto=socket.IPPROTO_TCP)
        return True
    except socket.gaierror:
        return False


def _generate_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')


@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    data  = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    name  = (data.get('name')  or '').strip()

    # 1. Format check (strict regex)
    if not _is_valid_email_format(email):
        return jsonify({'error': 'Invalid email format. Please enter a valid email address.'}), 400

    # 2. Disposable / throwaway domain check
    domain = email.split('@')[1]
    if domain in _DISPOSABLE_DOMAINS:
        return jsonify({'error': 'Disposable email addresses are not allowed. Please use a real email.'}), 400

    # 3. DNS existence check — catches completely fake domains
    if not _domain_has_dns(domain):
        return jsonify({'error': f'The email domain "@{domain}" does not exist. Please check your email address.'}), 400

    # 4. Already registered check
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Rate-limit: only one OTP per 60 seconds
    recent = (
        EmailOTP.query
        .filter_by(email=email)
        .order_by(EmailOTP.created_at.desc())
        .first()
    )
    if recent:
        elapsed = (datetime.utcnow() - recent.created_at).total_seconds()
        if elapsed < 60:
            wait = int(60 - elapsed)
            return jsonify({'error': f'Please wait {wait} seconds before requesting a new code.'}), 429

    # Invalidate all previous OTPs for this email
    EmailOTP.query.filter_by(email=email).delete()

    code = str(random.randint(100000, 999999))
    otp  = EmailOTP(
        email=email,
        otp_code=code,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.session.add(otp)
    db.session.commit()

    ok = send_otp_email(email, code, name)
    if not ok:
        return jsonify({'error': 'Failed to send verification email. Check your email address.'}), 500

    return jsonify({'sent': True}), 200


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data  = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    code  = (data.get('otp')   or '').strip()

    if not email or not code:
        return jsonify({'error': 'Email and OTP are required'}), 400

    otp = (
        EmailOTP.query
        .filter_by(email=email)
        .order_by(EmailOTP.created_at.desc())
        .first()
    )
    if not otp:
        return jsonify({'error': 'No verification code found. Please request a new one.'}), 400
    if otp.is_expired:
        return jsonify({'error': 'Code expired. Please request a new one.'}), 400
    if otp.otp_code != code:
        return jsonify({'error': 'Incorrect code. Please try again.'}), 400

    otp.verified_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'verified': True}), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    data     = request.get_json() or {}
    name     = (data.get('name')     or '').strip()
    email    = (data.get('email')    or '').strip().lower()
    password = data.get('password')  or ''

    if not name:
        return jsonify({'error': 'Name is required'}), 400
    if '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Require a verified OTP for this email (verified within the last 15 minutes)
    otp = (
        EmailOTP.query
        .filter_by(email=email)
        .order_by(EmailOTP.created_at.desc())
        .first()
    )
    if not otp or not otp.is_verified:
        return jsonify({'error': 'Email not verified. Please verify your email first.'}), 403
    if (datetime.utcnow() - otp.verified_at).total_seconds() > 900:
        return jsonify({'error': 'Verification expired. Please verify your email again.'}), 403

    password_hash = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
    user = User(name=name, email=email, password_hash=password_hash, is_verified=True)
    db.session.add(user)

    # Clean up used OTP
    EmailOTP.query.filter_by(email=email).delete()
    db.session.commit()

    send_welcome_email(user)

    return jsonify({'message': 'Registration successful'}), 201


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
    if not user:
        return jsonify({
            'error': 'No account found with this email address.',
            'code':  'EMAIL_NOT_FOUND',
        }), 401
    if not user.password_hash:
        return jsonify({
            'error': 'This account was created with Google. Please use "Continue with Google" to sign in.',
            'code':  'GOOGLE_ONLY',
        }), 401
    if not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({
            'error': 'Incorrect password. Please try again.',
            'code':  'WRONG_PASSWORD',
        }), 401

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
