"""
Test 2 — Authentication Endpoints
Tests cover:
  - Input validation (missing fields, short password, invalid email)
  - Disposable-email rejection
  - Login: user not found, wrong password, success
  - OTP-based registration flow validation
  - Protected-route access without a token
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from app.extensions import db
from app.models.email_otp import EmailOTP


# ── /api/auth/login ─────────────────────────────────────────────────────────

class TestLogin:

    def test_missing_email_and_password(self, client):
        """Should return 400 when both fields are missing."""
        response = client.post('/api/auth/login', json={})
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_missing_password(self, client):
        """Should return 400 when password is absent."""
        response = client.post('/api/auth/login',
                               json={'email': 'user@example.com'})
        assert response.status_code == 400

    def test_user_not_found(self, client):
        """Should return 401 with EMAIL_NOT_FOUND code for unknown email."""
        response = client.post('/api/auth/login',
                               json={'email': 'nobody@example.com',
                                     'password': 'whatever123'})
        assert response.status_code == 401
        data = response.get_json()
        assert data.get('code') == 'EMAIL_NOT_FOUND'

    def test_wrong_password(self, client, test_user):
        """Should return 401 with WRONG_PASSWORD code for bad password."""
        response = client.post('/api/auth/login',
                               json={'email': 'skinora_test@gmail.com',
                                     'password': 'wrongpassword!'})
        assert response.status_code == 401
        data = response.get_json()
        assert data.get('code') == 'WRONG_PASSWORD'

    def test_login_success(self, client, test_user):
        """Correct credentials must return 200 with an access_token and user object."""
        response = client.post('/api/auth/login',
                               json={'email': 'skinora_test@gmail.com',
                                     'password': 'TestPass123!'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'skinora_test@gmail.com'

    def test_login_returns_user_fields(self, client, test_user):
        """Response user object must include id, name, email."""
        response = client.post('/api/auth/login',
                               json={'email': 'skinora_test@gmail.com',
                                     'password': 'TestPass123!'})
        user = response.get_json()['user']
        assert 'id' in user
        assert 'name' in user
        assert 'email' in user


# ── /api/auth/register ───────────────────────────────────────────────────────

class TestRegister:

    def test_missing_name(self, client):
        """Should return 400 when name is not provided."""
        response = client.post('/api/auth/register',
                               json={'email': 'new@gmail.com',
                                     'password': 'Password123!'})
        assert response.status_code == 400
        assert 'Name' in response.get_json()['error']

    def test_password_too_short(self, client):
        """Should return 400 when password is less than 8 characters."""
        response = client.post('/api/auth/register',
                               json={'name': 'Test',
                                     'email': 'new@gmail.com',
                                     'password': 'short'})
        assert response.status_code == 400
        assert '8' in response.get_json()['error']

    def test_register_without_otp_verification(self, client):
        """Should return 403 when the email has no verified OTP."""
        response = client.post('/api/auth/register',
                               json={'name': 'New User',
                                     'email': 'notverified@gmail.com',
                                     'password': 'Password123!'})
        assert response.status_code == 403
        assert 'verified' in response.get_json()['error'].lower()

    def test_duplicate_email(self, client, test_user):
        """Should return 409 when registering an already-registered email."""
        response = client.post('/api/auth/register',
                               json={'name': 'Duplicate',
                                     'email': 'skinora_test@gmail.com',
                                     'password': 'Password123!'})
        assert response.status_code == 409

    def test_register_with_verified_otp(self, client, app):
        """Should return 201 when email has a fresh verified OTP."""
        email = 'otp_verified_user@gmail.com'
        with app.app_context():
            # Manually seed a verified OTP (simulates the OTP flow)
            otp = EmailOTP(
                email=email,
                otp_code='123456',
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                verified_at=datetime.utcnow(),
            )
            db.session.add(otp)
            db.session.commit()

        with patch('app.routes.auth.send_welcome_email'):
            response = client.post('/api/auth/register',
                                   json={'name': 'OTP User',
                                         'email': email,
                                         'password': 'SecurePass123!'})
        assert response.status_code == 201
        assert response.get_json()['message'] == 'Registration successful'


# ── /api/auth/send-otp ───────────────────────────────────────────────────────

class TestSendOtp:

    def test_invalid_email_format(self, client):
        """Should reject malformed email addresses before hitting DNS."""
        response = client.post('/api/auth/send-otp',
                               json={'email': 'not-an-email', 'name': 'Test'})
        assert response.status_code == 400
        assert 'Invalid email format' in response.get_json()['error']

    def test_disposable_email_rejected(self, client):
        """Should reject known disposable/throwaway email domains."""
        response = client.post('/api/auth/send-otp',
                               json={'email': 'user@mailinator.com', 'name': 'Test'})
        assert response.status_code == 400
        assert 'Disposable' in response.get_json()['error']

    def test_already_registered_email(self, client, test_user):
        """Should return 409 when the email is already registered."""
        response = client.post('/api/auth/send-otp',
                               json={'email': 'skinora_test@gmail.com', 'name': 'Test'})
        assert response.status_code == 409


# ── Token / Authorization ────────────────────────────────────────────────────

class TestTokenRequired:

    def test_no_auth_header(self, client):
        """Protected endpoint without Authorization header must return 401."""
        response = client.get('/api/tracking')
        assert response.status_code == 401
        assert 'error' in response.get_json()

    def test_malformed_token(self, client):
        """Malformed Bearer token must return 401."""
        response = client.get('/api/tracking',
                              headers={'Authorization': 'Bearer this.is.garbage'})
        assert response.status_code == 401

    def test_valid_token_grants_access(self, client, auth_headers):
        """Valid token must allow access to a protected endpoint."""
        response = client.get('/api/tracking', headers=auth_headers)
        # 200 means the token was accepted (empty list is fine)
        assert response.status_code == 200
