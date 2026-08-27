"""Fictional government-style scheme listing and matching.

All scheme data here is invented for the POC. None of it refers to a
real government program, and none of it links to a real application
portal.
"""

from flask import Blueprint, current_app, jsonify

from app.auth import require_auth

schemes_bp = Blueprint("schemes", __name__)

DEMO_SCHEMES = [
    {
        "scheme_name": "Rural Enterprise Growth Support — DEMO",
        "funding_summary": "Up to 40% capital subsidy on approved project cost (DEMO figure)",
        "required_documents": ["Enterprise profile", "Financial assessment"],
    },
    {
        "scheme_name": "Micro Business Development Assistance — DEMO",
        "funding_summary": "Low-interest working-capital loan support (DEMO figure)",
        "required_documents": ["Enterprise profile", "Feasibility report"],
    },
    {
        "scheme_name": "Rural Equipment Support Program — DEMO",
        "funding_summary": "Equipment grant covering up to 25% of asset cost (DEMO figure)",
        "required_documents": ["Enterprise profile", "Asset list"],
    },
]


@schemes_bp.get("/api/schemes")
@require_auth
def list_schemes():
    return jsonify({"schemes": DEMO_SCHEMES, "note": "DEMONSTRATION DATA ONLY"}), 200


@schemes_bp.post("/api/enterprises/<enterprise_id>/scheme-match")
@require_auth
def match_schemes(enterprise_id: str):
    enterprise = current_app.db.get_collection("enterprises").find_one(enterprise_id)
    if not enterprise:
        return jsonify({"error": "Enterprise not found"}), 404

    matches = []
    for scheme in DEMO_SCHEMES:
        matches.append(
            {
                "scheme_name": scheme["scheme_name"],
                "match_status": "eligible (demo)",
                "eligibility_summary": "Meets basic demo eligibility rules for this POC.",
                "required_documents": scheme["required_documents"],
                "funding_summary": scheme["funding_summary"],
            }
        )

    return (
        jsonify(
            {
                "enterprise_id": enterprise_id,
                "matches": matches,
                "note": "DEMONSTRATION DATA ONLY - not a real scheme eligibility decision.",
            }
        ),
        200,
    )
