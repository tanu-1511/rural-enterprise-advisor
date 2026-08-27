SAMPLE_ENTERPRISE = {
    "business_name": "Sunrise Dairy Co-op",
    "business_type": "Dairy processing",
    "location": "Sample District, Sample State",
    "target_customers": "Local households and small retailers",
    "margin_capital": 20000,
    "expected_investment": 100000,
    "available_assets": 15000,
    "workforce": 4,
    "revenue": 5000,
    "expenses": 3000,
    "existing_loans": 0,
}


def test_create_enterprise_succeeds(client, auth_headers):
    response = client.post(
        "/api/enterprises", json=SAMPLE_ENTERPRISE, headers=auth_headers
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["business_name"] == SAMPLE_ENTERPRISE["business_name"]
    assert "id" in body


def test_create_enterprise_missing_required_field_returns_400(client, auth_headers):
    payload = dict(SAMPLE_ENTERPRISE)
    del payload["business_name"]

    response = client.post("/api/enterprises", json=payload, headers=auth_headers)

    assert response.status_code == 400


def test_create_enterprise_with_negative_number_returns_400(client, auth_headers):
    payload = dict(SAMPLE_ENTERPRISE)
    payload["revenue"] = -500

    response = client.post("/api/enterprises", json=payload, headers=auth_headers)

    assert response.status_code == 400


def test_get_enterprise_by_id_returns_created_record(client, auth_headers):
    create_response = client.post(
        "/api/enterprises", json=SAMPLE_ENTERPRISE, headers=auth_headers
    )
    enterprise_id = create_response.get_json()["id"]

    get_response = client.get(
        f"/api/enterprises/{enterprise_id}", headers=auth_headers
    )

    assert get_response.status_code == 200
    assert get_response.get_json()["id"] == enterprise_id


def test_get_unknown_enterprise_returns_404(client, auth_headers):
    response = client.get("/api/enterprises/does-not-exist", headers=auth_headers)

    assert response.status_code == 404
