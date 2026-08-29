"""
Test 5 — Questionnaire Endpoints
Tests cover:
  - Authorization enforcement
  - Submitting answers — validation + successful response
  - Lifestyle summary endpoint
"""


class TestSubmitAnswers:

    def test_no_auth_returns_401(self, client):
        """POST /api/questionnaire/submit must be protected."""
        response = client.post('/api/questionnaire/submit',
                               json={'answers': {'sleep': 'good'}})
        assert response.status_code == 401

    def test_empty_answers_returns_400(self, client, auth_headers):
        """Should return 400 when answers dict is absent or empty."""
        response = client.post('/api/questionnaire/submit',
                               json={'answers': {}},
                               headers=auth_headers)
        assert response.status_code == 400
        assert 'answers' in response.get_json()['error'].lower()

    def test_missing_answers_key_returns_400(self, client, auth_headers):
        """Should return 400 when the answers key is not present at all."""
        response = client.post('/api/questionnaire/submit',
                               json={},
                               headers=auth_headers)
        assert response.status_code == 400

    def test_submit_answers_success(self, client, auth_headers):
        """Valid answers should return 200 with lifestyle summary and validation score."""
        payload = {
            'answers': {
                'sleep': 'poor',
                'water': 'low',
                'stress': 'high',
                'diet': 'no',
            },
            'skin_type': 'Oily',
            'acne_status': 'Acne',
        }
        response = client.post('/api/questionnaire/submit',
                               json=payload,
                               headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'lifestyle_summary' in data
        assert 'validation_score' in data
        assert 'validation_status' in data

    def test_submit_returns_advices(self, client, auth_headers):
        """Response should include an advices list."""
        payload = {
            'answers': {'sleep': 'good', 'water': 'adequate'},
            'skin_type': 'Normal',
            'acne_status': 'NoAcne',
        }
        response = client.post('/api/questionnaire/submit',
                               json=payload,
                               headers=auth_headers)
        assert response.status_code == 200
        assert 'advices' in response.get_json()
        assert isinstance(response.get_json()['advices'], list)


class TestGetLifestyle:

    def test_no_auth_returns_401(self, client):
        """GET /api/questionnaire/lifestyle must be protected."""
        response = client.get('/api/questionnaire/lifestyle')
        assert response.status_code == 401

    def test_lifestyle_returns_200(self, client, auth_headers):
        """Authenticated request should return 200 with a lifestyle key."""
        response = client.get('/api/questionnaire/lifestyle',
                              headers=auth_headers)
        assert response.status_code == 200
        assert 'lifestyle' in response.get_json()
