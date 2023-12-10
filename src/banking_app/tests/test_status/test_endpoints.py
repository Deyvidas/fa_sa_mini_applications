import pytest

from fastapi.testclient import TestClient

from src.banking_app.main import banking_app


client = TestClient(banking_app)


@pytest.mark.usefixtures('create_and_drop_tables')
class TestGET:

    def test_get_all_statuses(self):
        response = client.get('/status/list')
        assert response.status_code == 200
