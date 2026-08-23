from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "ContractIQ Backend is running successfully."


def test_login():
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@contractiq.com",
            "password": "Admin@12345",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_protected_endpoint_requires_authentication():
    response = client.get("/contracts")

    assert response.status_code == 401
