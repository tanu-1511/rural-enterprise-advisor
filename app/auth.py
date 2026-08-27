"""Minimal authentication for the POC.

A single demo user (see config.py) can log in and receive a short-lived
JWT. Protected endpoints use the `require_auth` decorator to check for a
valid `Authorization: Bearer <token>` header.

This is intentionally simple - there is no user database, password
hashing, refresh tokens, or role system. It exists to give the DevSecOps
pipeline something realistic to test (an auth flow, a signing secret from
the environment, and protected vs. unprotected routes).
"""

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Blueprint, current_app, jsonify, request

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _create_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=current_app.config["JWT_EXPIRY_MINUTES"]),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


@auth_bp.post("/login")
def login():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    if (
        username != current_app.config["DEMO_USERNAME"]
        or password != current_app.config["DEMO_PASSWORD"]
    ):
        return jsonify({"error": "Invalid credentials"}), 401

    token = _create_token(username)
    return jsonify({"access_token": token, "token_type": "bearer"}), 200


def require_auth(view_func):
    """Decorator that rejects requests without a valid bearer token."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "Authentication required"}), 401

        token = header.removeprefix("Bearer ").strip()
        try:
            jwt.decode(
                token, current_app.config["JWT_SECRET"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return view_func(*args, **kwargs)

    return wrapped
