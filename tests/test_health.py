"""
Test 1 — Health Check Endpoint
Verifies the /api/health endpoint confirms backend + database connectivity.
"""


def test_health_returns_200(client):
    """Health endpoint must return HTTP 200."""
    response = client.get('/api/health')
    assert response.status_code == 200


def test_health_db_connected(client):
    """Health endpoint must report the database as connected."""
    response = client.get('/api/health')
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['db'] == 'connected'
