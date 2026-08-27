from tests.test_enterprises import SAMPLE_ENTERPRISE


def _create_enterprise(client, auth_headers):
    response = client.post(
        "/api/enterprises", json=SAMPLE_ENTERPRISE, headers=auth_headers
    )
    return response.get_json()["id"]


def test_financial_assessment_returns_expected_fields(client, auth_headers):
    enterprise_id = _create_enterprise(client, auth_headers)

    response = client.post(
        f"/api/enterprises/{enterprise_id}/financial-assessment",
        json={
            "margin_capital": 20000,
            "project_cost": 100000,
            "requested_loan_amount": 80000,
            "interest_rate": 10,
            "loan_tenure_months": 12,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["loan_requirement"] == 80000
    assert body["estimated_emi"] > 0
    assert body["estimated_total_repayment"] > body["estimated_emi"]
    assert body["repayment_risk"] in {"low", "moderate", "high"}


def test_financial_assessment_for_unknown_enterprise_returns_404(client, auth_headers):
    response = client.post(
        "/api/enterprises/does-not-exist/financial-assessment",
        json={
            "margin_capital": 1000,
            "project_cost": 5000,
            "requested_loan_amount": 4000,
            "interest_rate": 8,
            "loan_tenure_months": 6,
        },
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_financial_assessment_with_invalid_input_returns_400(client, auth_headers):
    enterprise_id = _create_enterprise(client, auth_headers)

    response = client.post(
        f"/api/enterprises/{enterprise_id}/financial-assessment",
        json={
            "margin_capital": 1000,
            "project_cost": 5000,
            "requested_loan_amount": 4000,
            "interest_rate": 8,
            "loan_tenure_months": 0,
        },
        headers=auth_headers,
    )

    assert response.status_code == 400
