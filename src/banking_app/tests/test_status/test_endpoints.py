from fastapi.testclient import TestClient

from src.banking_app.main import banking_app


client = TestClient(banking_app)


def test_get_all_statuses():
    response = client.get('/status/list')
    assert response.status_code == 200
