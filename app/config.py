"""Application configuration.

All values come from environment variables so that nothing sensitive is
hardcoded in source code. See .env.example for the list of variables and
safe placeholder values.
"""

import os


def _str_to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    """Default configuration, used when running the app normally."""

    JWT_SECRET = os.environ.get("JWT_SECRET", "replace-with-local-development-secret")
    JWT_EXPIRY_MINUTES = int(os.environ.get("JWT_EXPIRY_MINUTES", "60"))

    MONGODB_URI = os.environ.get(
        "MONGODB_URI", "mongodb://localhost:27017/rural_enterprise_advisor"
    )
    # When true, an in-memory dictionary store is used instead of MongoDB.
    # This is convenient for local development or CI when MongoDB is not
    # running. It is turned on automatically for tests (see TestConfig).
    USE_IN_MEMORY_DB = _str_to_bool(os.environ.get("USE_IN_MEMORY_DB", "false"))

    # Demo-only credentials for the POC login endpoint. These are NOT
    # secrets - they are intentionally simple placeholder credentials for
    # a local proof-of-concept and must never be treated as real
    # authentication for production use.
    DEMO_USERNAME = os.environ.get("DEMO_USERNAME", "coordinator")
    DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "demo-password-123")


class TestConfig(Config):
    """Configuration used by the automated pytest suite."""

    USE_IN_MEMORY_DB = True
    JWT_SECRET = "test-only-secret"
    DEMO_USERNAME = "coordinator"
    DEMO_PASSWORD = "demo-password-123"
