"""CRUD endpoints for fictional rural enterprise profiles."""

from flask import Blueprint, current_app, jsonify, request

from app.auth import require_auth

enterprises_bp = Blueprint("enterprises", __name__, url_prefix="/api/enterprises")

REQUIRED_FIELDS = ["business_name", "business_type", "location"]

NUMERIC_FIELDS = [
    "margin_capital",
    "expected_investment",
    "available_assets",
    "workforce",
    "revenue",
    "expenses",
    "existing_loans",
]

ALLOWED_FIELDS = REQUIRED_FIELDS + NUMERIC_FIELDS + ["target_customers"]


def _validate_enterprise_payload(body: dict) -> str | None:
    """Returns an error message, or None if the payload is valid."""
    if not isinstance(body, dict):
        return "Request body must be a JSON object"

    for field in REQUIRED_FIELDS:
        value = body.get(field)
        if not value or not isinstance(value, str):
            return f"'{field}' is required and must be a non-empty string"

    for field in NUMERIC_FIELDS:
        if field not in body:
            continue
        value = body[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return f"'{field}' must be a number"
        if value < 0:
            return f"'{field}' must not be negative"

    return None


def _enterprises_collection():
    return current_app.db.get_collection("enterprises")


@enterprises_bp.post("")
@require_auth
def create_enterprise():
    body = request.get_json(silent=True)
    error = _validate_enterprise_payload(body)
    if error:
        return jsonify({"error": error}), 400

    record = {field: body[field] for field in ALLOWED_FIELDS if field in body}
    enterprise_id = _enterprises_collection().insert_one(record)
    created = _enterprises_collection().find_one(enterprise_id)
    return jsonify(created), 201


@enterprises_bp.get("")
@require_auth
def list_enterprises():
    return jsonify(_enterprises_collection().find_all()), 200


@enterprises_bp.get("/<enterprise_id>")
@require_auth
def get_enterprise(enterprise_id: str):
    enterprise = _enterprises_collection().find_one(enterprise_id)
    if not enterprise:
        return jsonify({"error": "Enterprise not found"}), 404
    return jsonify(enterprise), 200


@enterprises_bp.put("/<enterprise_id>")
@require_auth
def update_enterprise(enterprise_id: str):
    if not _enterprises_collection().find_one(enterprise_id):
        return jsonify({"error": "Enterprise not found"}), 404

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    updates = {field: body[field] for field in ALLOWED_FIELDS if field in body}
    if not updates:
        return jsonify({"error": "No valid fields provided to update"}), 400

    error = _validate_enterprise_payload({**_enterprises_collection().find_one(enterprise_id), **updates})
    if error:
        return jsonify({"error": error}), 400

    _enterprises_collection().update_one(enterprise_id, updates)
    return jsonify(_enterprises_collection().find_one(enterprise_id)), 200


@enterprises_bp.delete("/<enterprise_id>")
@require_auth
def delete_enterprise(enterprise_id: str):
    deleted = _enterprises_collection().delete_one(enterprise_id)
    if not deleted:
        return jsonify({"error": "Enterprise not found"}), 404
    return "", 204
