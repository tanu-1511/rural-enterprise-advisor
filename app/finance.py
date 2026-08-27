"""Financial assessment endpoint.

Performs simple, deterministic arithmetic (a standard EMI/loan formula) on
user-supplied numbers. No dynamic expression evaluation of any kind is
used - all calculations are plain Python arithmetic.
"""

from flask import Blueprint, current_app, jsonify, request

from app.auth import require_auth

finance_bp = Blueprint("finance", __name__, url_prefix="/api/enterprises")

REQUIRED_NUMERIC_FIELDS = [
    "margin_capital",
    "project_cost",
    "requested_loan_amount",
    "interest_rate",
    "loan_tenure_months",
]


def _validate_payload(body: dict) -> str | None:
    if not isinstance(body, dict):
        return "Request body must be a JSON object"

    for field in REQUIRED_NUMERIC_FIELDS:
        if field not in body:
            return f"'{field}' is required"
        value = body[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return f"'{field}' must be a number"
        if value < 0:
            return f"'{field}' must not be negative"

    if body["loan_tenure_months"] <= 0:
        return "'loan_tenure_months' must be greater than zero"

    return None


def _calculate_emi(principal: float, annual_rate_percent: float, tenure_months: int) -> float:
    """Standard reducing-balance EMI formula."""
    if annual_rate_percent == 0:
        return round(principal / tenure_months, 2)

    monthly_rate = (annual_rate_percent / 12) / 100
    growth = (1 + monthly_rate) ** tenure_months
    emi = principal * monthly_rate * growth / (growth - 1)
    return round(emi, 2)


def _risk_indicator(loan_requirement: float, project_cost: float) -> str:
    if project_cost == 0:
        return "unknown"
    ratio = loan_requirement / project_cost
    if ratio <= 0.5:
        return "low"
    if ratio <= 0.8:
        return "moderate"
    return "high"


@finance_bp.post("/<enterprise_id>/financial-assessment")
@require_auth
def financial_assessment(enterprise_id: str):
    if not current_app.db.get_collection("enterprises").find_one(enterprise_id):
        return jsonify({"error": "Enterprise not found"}), 404

    body = request.get_json(silent=True)
    error = _validate_payload(body)
    if error:
        return jsonify({"error": error}), 400

    margin_capital = float(body["margin_capital"])
    project_cost = float(body["project_cost"])
    requested_loan_amount = float(body["requested_loan_amount"])
    interest_rate = float(body["interest_rate"])
    tenure_months = int(body["loan_tenure_months"])

    beneficiary_contribution = margin_capital
    loan_requirement = max(project_cost - margin_capital, 0)
    loan_amount = min(requested_loan_amount, loan_requirement) or loan_requirement

    emi = _calculate_emi(loan_amount, interest_rate, tenure_months)
    total_repayment = round(emi * tenure_months, 2)
    monthly_operating_requirement = round(project_cost * 0.05, 2)

    result = {
        "enterprise_id": enterprise_id,
        "beneficiary_contribution": round(beneficiary_contribution, 2),
        "loan_requirement": round(loan_requirement, 2),
        "estimated_emi": emi,
        "estimated_total_repayment": total_repayment,
        "estimated_monthly_operating_requirement": monthly_operating_requirement,
        "repayment_risk": _risk_indicator(loan_requirement, project_cost),
        "note": "DEMO calculation for POC purposes only - not real financial advice.",
    }
    return jsonify(result), 200
