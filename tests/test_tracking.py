"""
Test 4 — Tracking Endpoints
Tests cover:
  - Authorization enforcement on all tracking routes
  - Creating a tracking plan (success + validation errors)
  - Toggling email reminders on/off
  - Check-in with invalid status
  - Dashboard and due-check endpoints
"""
import pytest
from unittest.mock import patch


class TestGetTracking:

    def test_no_auth_returns_401(self, client):
        """GET /api/tracking must be protected."""
        response = client.get('/api/tracking')
        assert response.status_code == 401

    def test_authenticated_returns_list(self, client, auth_headers):
        """Authenticated user should receive a list (may be empty)."""
        response = client.get('/api/tracking', headers=auth_headers)
        assert response.status_code == 200
        assert 'tracking' in response.get_json()
        assert isinstance(response.get_json()['tracking'], list)


class TestCreateTracking:

    def test_no_auth_returns_401(self, client):
        """POST /api/tracking/create must be protected."""
        response = client.post('/api/tracking/create', json={})
        assert response.status_code == 401

    def test_missing_remedy_id(self, client, auth_headers):
        """Should return 400 when remedy_id is not provided."""
        response = client.post('/api/tracking/create',
                               json={'frequency': 'weekly'},
                               headers=auth_headers)
        assert response.status_code == 400
        assert 'remedy_id' in response.get_json()['error']

    def test_invalid_frequency(self, client, auth_headers, test_remedy):
        """Should return 400 for unrecognised frequency values."""
        response = client.post('/api/tracking/create',
                               json={'remedy_id': test_remedy, 'frequency': 'daily'},
                               headers=auth_headers)
        assert response.status_code == 400

    def test_remedy_not_found(self, client, auth_headers):
        """Should return 404 when the given remedy_id does not exist."""
        response = client.post('/api/tracking/create',
                               json={'remedy_id': 99999, 'frequency': 'weekly'},
                               headers=auth_headers)
        assert response.status_code == 404

    def test_create_tracking_success(self, client, auth_headers, test_remedy):
        """Valid request should create a tracking plan and return 201."""
        with patch('app.routes.tracking.send_tracking_setup_email'):
            response = client.post('/api/tracking/create',
                                   json={'remedy_id': test_remedy,
                                         'frequency': 'weekly'},
                                   headers=auth_headers)
        assert response.status_code == 201
        data = response.get_json()
        assert 'tracking_id' in data
        assert 'next_reminder' in data

    def test_create_monthly_tracking(self, client, auth_headers, test_remedy):
        """Monthly frequency should also be accepted."""
        with patch('app.routes.tracking.send_tracking_setup_email'):
            response = client.post('/api/tracking/create',
                                   json={'remedy_id': test_remedy,
                                         'frequency': 'monthly'},
                                   headers=auth_headers)
        assert response.status_code == 201


class TestToggleReminders:

    def test_no_auth_returns_401(self, client):
        """PATCH /api/tracking/<id>/reminders must be protected."""
        response = client.patch('/api/tracking/1/reminders',
                                json={'paused': True})
        assert response.status_code == 401

    def test_tracking_not_found(self, client, auth_headers):
        """Should return 404 for a tracking ID that doesn't belong to the user."""
        response = client.patch('/api/tracking/99999/reminders',
                                json={'paused': True},
                                headers=auth_headers)
        assert response.status_code == 404

    def test_missing_paused_field(self, client, auth_headers, test_tracking):
        """Should return 400 when the 'paused' field is missing from the body."""
        response = client.patch(f'/api/tracking/{test_tracking}/reminders',
                                json={},
                                headers=auth_headers)
        assert response.status_code == 400
        assert 'paused' in response.get_json()['error']

    def test_pause_reminders(self, client, auth_headers, test_tracking):
        """Setting paused=True should disable reminders and return reminders_paused=True."""
        response = client.patch(f'/api/tracking/{test_tracking}/reminders',
                                json={'paused': True},
                                headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['reminders_paused'] is True

    def test_resume_reminders(self, client, auth_headers, test_tracking):
        """Setting paused=False should re-enable reminders."""
        response = client.patch(f'/api/tracking/{test_tracking}/reminders',
                                json={'paused': False},
                                headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['reminders_paused'] is False


class TestCheckin:

    def test_no_auth_returns_401(self, client):
        """POST /api/tracking/checkin must be protected."""
        response = client.post('/api/tracking/checkin',
                               json={'status': 'better'})
        assert response.status_code == 401

    def test_invalid_status(self, client, auth_headers):
        """Should return 400 for a status value outside the allowed set."""
        response = client.post('/api/tracking/checkin',
                               json={'status': 'fantastic'},
                               headers=auth_headers)
        assert response.status_code == 400


class TestDashboard:

    def test_no_auth_returns_401(self, client):
        """GET /api/tracking/dashboard must be protected."""
        response = client.get('/api/tracking/dashboard')
        assert response.status_code == 401

    def test_dashboard_returns_structure(self, client, auth_headers):
        """Dashboard must return user, detections, and trackings keys."""
        response = client.get('/api/tracking/dashboard', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert 'detections' in data
        assert 'trackings' in data


class TestDue:

    def test_no_auth_returns_401(self, client):
        """GET /api/tracking/due must be protected."""
        response = client.get('/api/tracking/due')
        assert response.status_code == 401

    def test_due_returns_boolean(self, client, auth_headers):
        """Response must include a boolean 'due' field."""
        response = client.get('/api/tracking/due', headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.get_json()['due'], bool)
