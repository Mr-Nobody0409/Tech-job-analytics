from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Tech Job Analytics API is running"

def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "database" in data