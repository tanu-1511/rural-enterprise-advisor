"""Flask application factory for the Rural Enterprise Advisory API."""

from dotenv import load_dotenv
from flask import Flask, jsonify

from app.config import Config
from app.extensions import Database


def create_app(config_class=Config) -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(config_class)

    app.db = Database(
        use_in_memory=app.config["USE_IN_MEMORY_DB"],
        mongo_uri=app.config["MONGODB_URI"],
    )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(_error):
        # Deliberately generic: never leak stack traces or internal
        # details to API clients.
        return jsonify({"error": "Internal server error"}), 500

    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.enterprises import enterprises_bp
    from app.feasibility import feasibility_bp
    from app.finance import finance_bp
    from app.schemes import schemes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(enterprises_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(feasibility_bp)
    app.register_blueprint(schemes_bp)
    app.register_blueprint(dashboard_bp)

    return app
