from app.config import TestConfig


def test_login_with_valid_credentials_returns_token(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": TestConfig.DEMO_USERNAME,
            "password": TestConfig.DEMO_PASSWORD,
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_with_invalid_credentials_is_rejected(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "wrong-user", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_login_with_missing_fields_returns_400(client):
    response = client.post("/api/auth/login", json={"username": "coordinator"})

    assert response.status_code == 400


def test_protected_endpoint_without_token_is_rejected(client):
    response = client.get("/api/enterprises")

    assert response.status_code == 401


def test_protected_endpoint_with_valid_token_succeeds(client, auth_headers):
    response = client.get("/api/enterprises", headers=auth_headers)

    assert response.status_code == 200
