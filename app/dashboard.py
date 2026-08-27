"""Aggregated dashboard summary for coordinators.

Combines the number of stored enterprises with a couple of fixed demo
figures, so the endpoint has real, authenticated, database-backed
behaviour without needing extra business logic.
"""

from flask import Blueprint, current_app, jsonify

from app.auth import require_auth

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("/summary")
@require_auth
def dashboard_summary():
    enterprises = current_app.db.get_collection("enterprises").find_all()
    total = len(enterprises)

    summary = {
        "total_enterprises": total,
        "assessed": min(total, max(total - 2, 0)),
        "high_risk": min(total, 1) if total else 0,
        "funding_facilitated": min(total, 1) if total else 0,
        "pending_documents": max(total - 1, 0),
        "note": "DEMO aggregation for POC purposes only.",
    }
    return jsonify(summary), 200
