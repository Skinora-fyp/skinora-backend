"""
Test 3 — Remedies Endpoints
Tests cover:
  - Authorization enforcement
  - Missing required query parameter
  - Successful remedy listing by condition
  - 404 for a non-existent remedy ID
"""


class TestListRemedies:

    def test_no_auth_returns_401(self, client):
        """Remedies list must be protected — unauthenticated request returns 401."""
        response = client.get('/api/remedies?final_condition=Oily_Acne')
        assert response.status_code == 401

    def test_missing_condition_param(self, client, auth_headers):
        """Should return 400 when final_condition query param is absent."""
        response = client.get('/api/remedies', headers=auth_headers)
        assert response.status_code == 400
        assert 'final_condition' in response.get_json()['error']

    def test_returns_remedies_for_condition(self, client, auth_headers, test_remedy):
        """Should return 200 with a remedies list for a known condition."""
        response = client.get('/api/remedies?final_condition=Oily_Acne',
                              headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'remedies' in data
        assert isinstance(data['remedies'], list)
        assert len(data['remedies']) >= 1

    def test_remedies_contain_required_fields(self, client, auth_headers, test_remedy):
        """Each remedy in the response must include id, name, and instructions."""
        response = client.get('/api/remedies?final_condition=Oily_Acne',
                              headers=auth_headers)
        remedies = response.get_json()['remedies']
        for remedy in remedies:
            assert 'id' in remedy
            assert 'name' in remedy
            assert 'instructions' in remedy

    def test_unknown_condition_returns_empty_list(self, client, auth_headers):
        """An unrecognised condition should return 200 with an empty remedies list."""
        response = client.get('/api/remedies?final_condition=Unknown_Condition',
                              headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()['remedies'] == []

    def test_final_condition_echoed_in_response(self, client, auth_headers, test_remedy):
        """The response should echo back the final_condition that was queried."""
        response = client.get('/api/remedies?final_condition=Oily_Acne',
                              headers=auth_headers)
        assert response.get_json()['final_condition'] == 'Oily_Acne'


class TestGetRemedyById:

    def test_remedy_not_found(self, client, auth_headers):
        """Should return 404 for a remedy ID that does not exist."""
        response = client.get('/api/remedies/99999', headers=auth_headers)
        assert response.status_code == 404
        assert 'error' in response.get_json()

    def test_no_auth_returns_401(self, client):
        """Getting a remedy by ID must also be protected."""
        response = client.get('/api/remedies/1')
        assert response.status_code == 401
